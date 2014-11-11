import os
from math import ceil, log10
from celery.utils.log import get_task_logger
import simplekml
import colander
from sqlalchemy import func, cast, Numeric
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Speed, getGPSCount
from script_wrapper.validation import validateRange


logger = get_task_logger(__name__)


def colorValidator(node, value):
    if (value[0] != '#'):
        raise colander.Invalid(node,
              '%r is not a color, should be #RRGGBB' % value)

    if int('000000', 16) <= int(value[1:], 16) <= int('FFFFFF', 16):
        pass
    else:
        raise colander.Invalid(node,
              '%r is not a color, should be #RRGGBB' % value)


class Color(colander.MappingSchema):
    slowest = colander.SchemaNode(colander.String())
    slow = colander.SchemaNode(colander.String())
    fast = colander.SchemaNode(colander.String())
    fastest = colander.SchemaNode(colander.String())


class Tracker(colander.MappingSchema):
    id = colander.SchemaNode(colander.Int())
    color = Color()


class Trackers(colander.SequenceSchema):
    tracker = Tracker()


class Schema(colander.MappingSchema):
    start = colander.SchemaNode(colander.DateTime())
    end = colander.SchemaNode(colander.DateTime())
    trackers = Trackers()
    shape = colander.SchemaNode(colander.String(),
                                validator=colander.OneOf(['circle', 'iarrow', 'tarrow']))
    size = colander.SchemaNode(colander.String(),
                               validator=colander.OneOf(['small', 'medium', 'large']))
    sizebyalt = colander.SchemaNode(colander.Boolean(), missing=False)
    colorby = colander.SchemaNode(colander.String(),
                               validator=colander.OneOf(['fixed', 'ispeed', 'tspeed']))
    speedthreshold1 = colander.SchemaNode(colander.Int(), missing=5)
    speedthreshold2 = colander.SchemaNode(colander.Int(), missing=10)
    speedthreshold3 = colander.SchemaNode(colander.Int(), missing=20)
    alpha = colander.SchemaNode(colander.Int(),
                                validator=colander.Range(0, 100))
    valid_alt_modes = ['absolute', 'clampToGround', 'relativeToGround']
    altitudemode = colander.SchemaNode(colander.String(),
                                       validator=colander.OneOf(valid_alt_modes))


class PyKML(PythonTask):
    """Generate a KMZ file with multiple trackers using simplekml package"""
    name = 'kmzgen'
    label = 'KMZ generator'
    description = 'Generate a KMZ file with multiple trackers.'
    autoregister = True
    MAX_FIX_COUNT = 50000
    MAX_FIX_TOTAL_COUNT = 50000
    pointstylecache = {}

    def run(self, db_url, trackers, start, end,
            shape, size, sizebyalt, colorby,
            speedthreshold1, speedthreshold2, speedthreshold3,
            alpha, altitudemode):
        self.update_state(state="RUNNING")
        db_url = self.local_db_url(db_url)
        logger.info(db_url)
        session = DBSession(db_url)()

        trackers_list = "_".join([str(t['id']) for t in trackers])
        filename_tpl = "{start}-{end}-{trackers}.kmz"
        filename = filename_tpl.format(start=start,
                                       end=end,
                                       trackers=trackers_list,
                                       )
        fn = os.path.join(self.output_dir(), filename)
        kml = simplekml.Kml(open=0)

        self.pointstylecache = {}
        style = {'shape': shape,
                 'size': size,
                 'sizebyalt': sizebyalt,
                 'colorby': colorby,
                 'speedthresholds': [speedthreshold1,
                                    speedthreshold2,
                                    speedthreshold3],
                 'alpha': alpha,
                 'altitudemode': altitudemode,
                 }
        self.addIcon2kml(kml, style)
        for tracker in trackers:
            self.track2kml(kml, session,
                           start, end,
                           tracker,
                           style)

        session.close()
        kml.savekmz(fn)

        result = {}
        result['query'] = {'start': start.isoformat(),
                           'end': end.isoformat(),
                           'trackers': trackers,
                           'style': style,
                           }
        return result

    def addIcon2kml(self, kml, style):
        if style['shape'] == 'circle':
            return kml.addfile(os.path.join(self.task_dir(), 'circle.png'))
        else:
            return kml.addfile(os.path.join(self.task_dir(), 'arrow.png'))

    def fetchtrack(self, session,
                   tracker_id, start, end,
                   need_traject_speed,
                   need_traject_direction,
                   need_elevation,
                   ):
        """Fetch track data from db"""
        tid = Speed.device_info_serial
        dt = Speed.date_time
        if need_elevation:
            elev = Speed.elevation
        else:
            # column is ignored, but for unpacking return same number of columns
            elev = Speed.altitude
        q = session.query(tid, dt,
                          Speed.longitude,
                          Speed.latitude,
                          Speed.altitude,
                          func.round(cast(Speed.speed, Numeric), 2),
                          Speed.trajectSpeed,
                          func.round(Speed.direction ,2),
                          Speed.trajectDirection,
                          elev,
                          )
        q = q.filter(tid == tracker_id)
        q = q.filter(dt.between(start.isoformat(), end.isoformat()))
        q = q.filter(Speed.longitude != None)
        q = q.filter(Speed.direction != None)
        q = q.filter(Speed.userflag == 0)
        q = q.order_by(dt)
        return q

    def track2kml(self, kml, session,
                  start, end,
                  tracker,
                  style):
        need_traject_speed = style['colorby'] == 'tspeed'
        need_traject_direction = style['shape'] == 'tarrow'
        need_elevation = style['altitudemode'] == 'relativeToGround'
        tracker_id = tracker['id']
        rows = self.fetchtrack(session,
                               tracker_id, start, end,
                               need_traject_speed,
                               need_traject_direction,
                               need_elevation,
                               )

        self.trackrows2kml(kml, rows, tracker, style)

    def trackrows2kml(self, kml, rows, tracker, style):
        tpl = """
        <table border="0">
        <tr><td>ID</td><td>{tid}</td></tr>
        <tr><td>Time</td><td>{dt}</td></tr>
        <tr><td>Lon, Lat (&deg;)</td><td>{lon:.3f}, {lat:.3f}</td></tr>
        <tr><td>Altitude (m)</td><td>{alt}</td></tr>
        <tr><td>Instantanous speed (m/s)</td><td>{ispeed:.1f}</td></tr>
        <tr><td>Traject speed (m/s)</td><td>{tspeed}</td></tr>
        <tr><td>Instantanous direction (&deg;)</td><td>{idir:.1f}</td></tr>
        <tr><td>Traject direction (&deg;)</td><td>{tdir}</td></tr>
        </table>
        """

        color_scheme = tracker['color']
        alpha = style['alpha']

        folder = kml.newfolder(name='tracker-' + str(tracker['id']), open=1)
        pfolder = folder.newfolder(name='points', open=0)

        parts = []
        for row in rows:
            (tid, dt, lon, lat, alt, ispeed, tspeed, idirection, tdirection, elevation,) = row
            if tdirection > 180:
                tdirection = tdirection - 360
            parts.append((lon, lat))
            pnt = pfolder.newpoint()

            if style['altitudemode'] == 'relativeToGround':
                # change absolute alt to relative to ground elevation
                alt = alt - elevation

            pnt.style = self.kmlstyle4point(ispeed, tspeed, idirection, tdirection, alt, style, color_scheme)
            pnt.description = tpl.format(tid=tid, dt=dt,
                                         lon=lon, lat=lat, alt=alt,
                                         ispeed=ispeed, idir=idirection,
                                         tspeed=tspeed, tdir=tdirection,
                                         )
            pnt.timestamp.when = dt.isoformat()
            pnt.coords = [(lon, lat, alt)]
            pnt.extrude = 1

            pnt.altitudemode = style['altitudemode']
            if (style['altitudemode'] == 'absolute' and alt < 10):
                # Don't put point under ground
                pnt.altitudemode = simplekml.AltitudeMode.clamptoground

        line = folder.newlinestring()
        line.style.linestyle.width = 1
        line.style.linestyle.color = self.color4line(color_scheme, alpha)
        line.coords = parts

    def color4line(self, color_scheme, alpha):
        color = color_scheme['fast']
        return self.webcolor2kmlcolor(color, alpha)

    def webcolor2kmlcolor(self, webcolor, alpha):
        webcolor = webcolor.lower()
        opacity = hex(int(ceil(alpha * 2.55)))[2:4]
        # convert #rrggbb to aabbggrr
        kmlcolor = opacity + webcolor[5:7] + webcolor[3:5] + webcolor[1:3]
        return kmlcolor

    def kmlcolor4point(self, color_scheme, style, speed):
        if style['colorby'] in ('ispeed', 'tspeed'):
            webcolor = color_scheme['fastest']
            if speed < style['speedthresholds'][2]:
                webcolor = color_scheme['fast']
            if speed < style['speedthresholds'][1]:
                webcolor = color_scheme['slow']
            if speed < style['speedthresholds'][0]:
                webcolor = color_scheme['slowest']
        else:
            webcolor = color_scheme['fast']
        return self.webcolor2kmlcolor(webcolor, style['alpha'])

    def hashcode4pointstyle(self, color, direction, scale, style):
        return str([color, direction, scale, style])

    def size2iconscale(self, size, sizebyalt, altitude):
        # default altitude, when sizebyalt is not requested
        if not sizebyalt:
            altitude = 10

        # cant have log10 < 1, so clip alt to 1
        if altitude < 1:
            altitude = 1

        if size == 'small':
            scale = 0.3 * log10(altitude) + 0.2
        elif size == 'medium':
            scale = 0.6 * log10(altitude) + 0.1
        elif size == 'large':
            scale = 0.7 * log10(altitude) + 0.4

        return scale

    def kmlstyle4point(self, ispeed, tspeed, idirection, tdirection, altitude, style, color_scheme):
        direction = idirection
        if style['shape'] == 'tarrow':
            direction = tdirection
        speed = ispeed
        if style['colorby'] == 'tspeed':
            speed = tspeed
        scale = self.size2iconscale(style['size'], style['sizebyalt'], altitude)
        color = self.kmlcolor4point(color_scheme, style, speed)

        id = self.hashcode4pointstyle(color, direction, scale, style)
        if id in self.pointstylecache:
            return self.pointstylecache[id]

        kmlstyle = simplekml.Style()

        if style['shape'] in ('iarrow', 'tarrow'):
            kmlstyle.iconstyle.icon.href = 'files/arrow.png'
            kmlstyle.iconstyle.heading = direction
        else:
            kmlstyle.iconstyle.icon.href = 'files/circle.png'
            scale = scale * 0.5

        kmlstyle.iconstyle.scale = scale
        kmlstyle.iconstyle.color = color

        self.pointstylecache[id] = kmlstyle
        return kmlstyle

    def formfields2taskargs(self, fields, db_url):
        # form has transparency and kml requires opacity aka alpha
        fields['alpha'] = abs(100 - fields['transparency'])
        del(fields['transparency'])

        schema = Schema()
        taskargs = schema.deserialize(fields)

        # Test if selection will give results
        total_gps_count = 0
        for tracker in taskargs['trackers']:
            gps_count = getGPSCount(db_url, tracker['id'],
                                    taskargs['start'], taskargs['end'])
            total_gps_count += gps_count
            validateRange(gps_count, 0, self.MAX_FIX_COUNT, tracker['id'])
        validateRange(total_gps_count, 0, self.MAX_FIX_TOTAL_COUNT)

        taskargs['db_url'] = db_url
        return taskargs
