import time
import json
import os
from celery import Task
from celery import current_task
from celery import current_app
from celery.utils.log import get_task_logger
import iso8601
import simplekml
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Speed, getGPSCount
from script_wrapper.validation import validateRange

logger = get_task_logger(__name__)


class PyKML(PythonTask):
    name = 'kmlpy'
    label = 'Generate KMZ file'
    description = 'Using python'
    autoregister = True

    def run(self, db_url, tracker_id, start, end):
        self.update_state(state="RUNNING")
        fn = os.path.join(self.output_dir(), 'result.kmz')

        # Perform a database query
        s = DBSession(db_url)
        tid = Speed.device_info_serial
        dt = Speed.date_time
        q = s().query(tid, dt,
                      Speed.longitude,
                      Speed.latitude,
                      Speed.altitude,
                      Speed.speed,
                      Speed.direction
                      )
        q = q.filter(tid == tracker_id)
        q = q.filter(dt.between(start, end))
        q = q.filter(Speed.longitude!=None)
        q = q.filter(Speed.direction!=None)
        q = q.order_by(dt)

        kml = simplekml.Kml()

        colors = ['ffbeffff','ff00ffff','ff00b9b9', 'ff007373']
        styles = []
        for color in colors:
            style = simplekml.Style()
            style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal2/icon26.png'
            style.iconstyle.scale = 0.4
            style.iconstyle.color = color
            styles.append(style)

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

        parts = []
        for tid, dt, lon, lat, alt, spd, dire in q.all():
            parts.append((lon, lat))
            pnt = kml.newpoint()
            pnt.style = styles[self.speed2styleId(spd)]
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

        line = kml.newlinestring()
        line.style.linestyle.width = 1
        line.style.linestyle.color = 'ff00ffff'
        line.coords = parts

        kml.savekmz(fn)

        result = {}
        result['query'] = {'start': start.isoformat(),
                           'end': end.isoformat(),
                           'tracker_id': tracker_id,
                           }

        return result

    def speed2styleId(self, spd):
        """Speed is canned into 4 color styles"""
        sid = 3
        if spd < 20:
            sid = 2
        if spd < 10:
            sid = 1
        if spd < 5:
            sid = 0
        return sid

    def formfields2taskargs(self, fields, db_url):
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        tracker_id = fields['id']

        # Test if selection will give results
        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, 50000)

        return {'db_url':  db_url,
                'start': start,
                'end': end,
                'tracker_id': tracker_id,
                }
