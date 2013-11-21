import os
from celery.utils.log import get_task_logger
import iso8601
import simplekml
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Speed, getGPSCount
from script_wrapper.validation import validateRange

logger = get_task_logger(__name__)


class PyKML(PythonTask):
    """Generate a KMZ file with multiple trackers using simplekml package"""
    name = 'kmlpy'
    label = 'KMZ file'
    description = 'Generate a KMZ file with multiple trackers.'
    autoregister = True
    MAX_FIX_COUNT = 50000
    MAX_FIX_TOTAL_COUNT = 50000

    def run(self, db_url, trackers, start, end):
        self.update_state(state="RUNNING")
        db_url = self.local_db_url(db_url)
        session = DBSession(db_url)()

        trackers_list = "_".join([str(t['id']) for t in trackers])
        filename_tpl = "{start}-{end}-{trackers}.kmz"
        filename = filename_tpl.format(start=start,
                                       end=end,
                                       trackers=trackers_list,
                                       )
        fn = os.path.join(self.output_dir(), filename)
        kml = simplekml.Kml(open=0)
        styles = self.create_styles()
        for tracker in trackers:
            self.track2kml(kml, session, styles,
                           tracker['id'], tracker['color'],
                           start, end)

        session.close()
        kml.savekmz(fn)

        result = {}
        result['query'] = {'start': start.isoformat(),
                           'end': end.isoformat(),
                           'trackers': trackers,
                           }
        return result

    def track2kml(self, kml, session, styles,
                  tracker_id, base_color,
                  start, end):
        # Perform a database query
        tid = Speed.device_info_serial
        dt = Speed.date_time
        q = session.query(tid, dt,
                          Speed.longitude,
                          Speed.latitude,
                          Speed.altitude,
                          Speed.speed,
                          Speed.direction,
                          )
        q = q.filter(tid == tracker_id)
        q = q.filter(dt.between(start, end))
        q = q.filter(Speed.longitude != None)
        q = q.filter(Speed.direction != None)
        q = q.order_by(dt)

        tpl = """
        <table border="0">
        <tr><td>ID</td><td>{tid}</td></tr>
        <tr><td>Time (UTC)</td><td>{dt}</td></tr>
        <tr><td>Lon, Lat (&deg;)</td><td>{lon:.3f}, {lat:.3f}</td></tr>
        <tr><td>Altitude (m)</td><td>{alt}</td></tr>
        <tr><td>Speed (km/h)</td><td>{spd:.1f}</td></tr>
        <tr><td>Heading (&deg;)</td><td>{dir:.1f}</td></tr>
        </table>
        """

        folder = kml.newfolder(name=str(tracker_id), open=1)

        parts = []
        for tid, dt, lon, lat, alt, spd, dire in q.all():
            parts.append((lon, lat))
            pnt = folder.newpoint()
            pnt.style = self.speed2style(styles, base_color, spd)
            pnt.description = tpl.format(tid=tid, dt=dt,
                                         lon=lon, lat=lat, alt=alt,
                                         spd=spd, dir=dire,
                                         )
            pnt.timestamp.when = dt.isoformat()
            pnt.coords = [(lon, lat, alt)]
            pnt.extrude = 1
            if alt > 2:
                pnt.altitudemode = simplekml.AltitudeMode.absolute
            else:
                # Don't put point under ground
                pnt.altitudemode = simplekml.AltitudeMode.clamptoground

        line = folder.newlinestring()
        line.style.linestyle.width = 1
        line.style.linestyle.color = 'ff00ffff'
        line.coords = parts

    def create_styles(self):
        color_schemes = [
                           ['FFFFFF50','FFFDD017','FFC68E17', 'FF733C00'],  # OK GEEL -DONKERGEEL
                           ['FFF7E8AA','FFF9E070','FFFCB514', 'FFA37F14'],  # OK GEEL -GEELGROEN
                           ['FFFFA550','FFEB4100','FFFF0000', 'FF7D0000'],  # OK ORANJE ROOD
                           ['FF5A5AFF','FF0000FF','FF0000AF', 'FF00004B'],  # OK FEL BLAUW
                           ['FFBEFFFF','FF00FFFF','FF00B9B9', 'FF007373'],  # OK LICHT BLAUW
                           ['FF8CFF8C','FF00FF00','FF00B900', 'FF004B00'],  #  FEL GROEN
                           ['FFFF8CFF','FFFF00FF','FFA500A5', 'FF4B004B'],  #  OK PAARS
                           ['FFAADD96','FF60C659','FF339E35', 'FF3A7728'],  # OK GROEN
                           ['FFFFD3AA','FFF9BA82','FFF28411', 'FFBF5B00'],  # OK
                           ['FFC6C699','FFAAAD75','FF6B702B', 'FF424716'],  # OK
                           ['FFE5BFC6','FFD39EAF','FFA05175', 'FF7F284F'],  # OK  ROZE-PAARS
                           ['FFDADADA','FFC3C3C3','FF999999', 'FF3C3C3C'],  #  VAN WIT NAAR DONKERGRIJS
                           ['FFC6B5C4','FFA893AD','FF664975', 'FF472B59'],  # OK BLAUWPAARS
                           ['FFC1D1BF','FF7FA08C','FF5B8772', 'FF21543F'],  # OK GRIJSGROEN
                           ['FF000000','FF000000','7D000000', '10000000'],  # BLACK
                        ]

        styles = {}
        for idx, color_scheme in enumerate(color_schemes):
            styles[color_scheme[0][2:8]] = []
            for color in color_scheme:
                style = simplekml.Style()
                style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal2/icon26.png'
                style.iconstyle.scale = 0.4
                # convert frgb to fbgr
                style.iconstyle.color = color[0:2] + color[6:8] + color[4:6] + color[2:4]
                styles[color_scheme[0][2:8]].insert(idx, style)

        return styles

    def speed2style(self, styles, base_color, spd):
        """Color of point is dependent on base_color and speed"""
        color_scheme = styles[base_color]

        style = color_scheme[0]
        if spd < 20:
            style = color_scheme[1]
        if spd < 10:
            style = color_scheme[2]
        if spd < 5:
            style = color_scheme[3]

        return style

    def formfields2taskargs(self, fields, db_url):
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        trackers = fields['trackers']

        # Test if selection will give results
        total_gps_count = 0
        for tracker in trackers:
            gps_count = getGPSCount(db_url, tracker['id'], start, end)
            total_gps_count += gps_count
            validateRange(gps_count, 0, self.MAX_FIX_COUNT)
        validateRange(total_gps_count, 0, self.MAX_FIX_TOTAL_COUNT)

        return {'db_url':  db_url,
                'start': start,
                'end': end,
                'trackers': trackers,
                }
