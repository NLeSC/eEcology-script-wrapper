from datetime import datetime
import unittest
from mock import patch
from colander.iso8601 import UTC
from colander import Invalid
import simplekml
import simplekml.featgeom
import simplekml.timeprimitive
import simplekml.substyle
import simplekml.styleselector
from script_wrapper.tasks.pykml import PyKML


class Test(unittest.TestCase):

    def setUp(self):
        # simplekml uses class counters, reset them to 0 before each test
        # so tests are not order dependent
        simplekml.featgeom.Feature._id = 0
        simplekml.featgeom.Geometry._id = 0
        simplekml.Link._id = 0
        simplekml.substyle.ColorStyle._id = 0
        simplekml.BalloonStyle._id = 0
        simplekml.ListStyle._id = 0
        simplekml.styleselector.StyleSelector._id = 0
        simplekml.timeprimitive.TimePrimitive._id = 0

    @patch('script_wrapper.tasks.pykml.getGPSCount')
    def test_formfields2taskargs_noerrors(self, gpscount):
        gpscount.return_value = 400
        task = PyKML()
        color = {'id': 3,
                 'slowest': '#FFFF50',
                 'slow': '#FDD017',
                 'fast': '#C68E17',
                 'fastest': '#733C00'
                 }
        formfields = {
                      'start': '2013-05-14T10:11:12Z',
                      'end': '2013-05-15T08:33:34Z',
                      'trackers': [{'id': 1234, 'color': color}],
                      'shape': 'circle',
                      'size': 'medium',
                      'colorby': 'ispeed',
                      'speedthreshold1': 5,
                      'speedthreshold2': 10,
                      'speedthreshold3': 20,
                      'alpha': 100,
                      'altitudemode': 'absolute',
                      }
        db_url = 'postgresql://localhost/eecology'
        taskargs = task.formfields2taskargs(formfields, db_url)

        ecolor = {'slowest': '#FFFF50',
                  'slow': '#FDD017',
                  'fast': '#C68E17',
                  'fastest': '#733C00'
                  }
        etaskargs = {'db_url': 'postgresql://localhost/eecology',
                     'end': datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                     'start': datetime(2013, 5, 14, 10, 11, 12, tzinfo=UTC),
                     'trackers': [{'id': 1234, 'color': ecolor}],
                      'shape': 'circle',
                      'size': 'medium',
                      'sizebyalt': 'off',
                      'colorby': 'ispeed',
                      'speedthreshold1': 5,
                      'speedthreshold2': 10,
                      'speedthreshold3': 20,
                      'alpha': 100,
                      'altitudemode': 'absolute',
                     }
        self.assertDictEqual(taskargs, etaskargs)

    def test_formfields2taskargs_wrongshape(self):
        task = PyKML()
        color = {'id': 3,
                 'slowest': '#FFFF50',
                 'slow': '#FDD017',
                 'fast': '#C68E17',
                 'fastest': '#733C00'
                 }
        formfields = {
                      'start': '2013-05-14T10:11:12Z',
                      'end': '2013-05-15T08:33:34Z',
                      'trackers': [{'id': 1234, 'color': color}],
                      # wrong shape
                      'shape': 'square',
                      'size': 'medium',
                      'colorby': 'ispeed',
                      'speedthreshold1': 5,
                      'speedthreshold2': 10,
                      'speedthreshold3': 20,
                      'alpha': 100,
                      'altitudemode': 'absolute',
                      }
        db_url = 'postgresql://localhost/eecology'
        with self.assertRaises(Invalid) as e:
            task.formfields2taskargs(formfields, db_url)

        expected = {
                    'shape': u'"square" is not one of circle, iarrow, tarrow'
                    }
        self.assertEqual(e.exception.asdict(), expected)

    def test_addIcon2kml_circlepngadded(self):
        kml = simplekml.Kml()
        task = PyKML()
        style = {'shape': 'circle'}

        path = task.addIcon2kml(kml, style)

        self.assertEqual(path, 'files/circle.png')

    def test_addIcon2kml_arrowpngadded(self):
        kml = simplekml.Kml()
        task = PyKML()
        style = {'shape': 'iarrow'}

        path = task.addIcon2kml(kml, style)

        self.assertEqual(path, 'files/arrow.png')

    def test_trackrows2kml_2pointswithdefaultstyle(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                [355, datetime(2013, 5, 15, 8, 34, 34, tzinfo=UTC),
                 4.485608, 52.415252, 34,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff17d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
                <Placemark id="feat_5">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:34:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.415&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;34&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_1">
                        <when>2013-05-15T08:34:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_1">
                        <coordinates>4.485608,52.415252,34</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_6">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_2">
                    <coordinates>4.485608,52.412252,0.0 4.485608,52.415252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_singlepointwithdefaultstyle(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_0">
                <LineStyle id="substyle_0">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff17d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_0</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_negativealt_clamped(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, -5,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_0">
                <LineStyle id="substyle_0">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff17d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;-5&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,-5</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>clampToGround</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_0</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_speedzero_slowestcolor(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 0.0, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff50ffff</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;0.0&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_halftransparent(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 50,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>80178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>8017d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_fixedcolor_fastcolor(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'fixed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff178ec6</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_shapeiarrow_arrowwithheadingasicon(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                ]
        style = {'shape': 'iarrow',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff17d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>14.1</heading>
                        <Icon id="link_0">
                            <href>files/arrow.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_fastestspeed_fastestcolor(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 28.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff003c73</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;28.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_fastspeed_fastcolor(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 18.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'off',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff178ec6</color>
                        <colorMode>normal</colorMode>
                        <scale>0.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;18.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_sizebyalton_iconsizebig(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': 'on',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff17d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>50.5</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_sizebyaltonlargesize_iconsizebig(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'large',
                 'sizebyalt': 'on',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff17d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>59.2</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.maxDiff =None
        self.assertMultiLineEqual(kmlstr, expected)

    def test_trackrows2kml_sizebyaltonsmallsize_iconsizebig(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 14.1],
                ]
        style = {'shape': 'circle',
                 'size': 'small',
                 'sizebyalt': 'on',
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        kmlstr = kml.kml()
        self.maxDiff =None

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Folder id="feat_2">
            <Style id="stylesel_1">
                <LineStyle id="substyle_1">
                    <color>ff178ec6</color>
                    <colorMode>normal</colorMode>
                    <width>1</width>
                </LineStyle>
            </Style>
            <name>tracker-355</name>
            <open>1</open>
            <Folder id="feat_3">
                <Style id="stylesel_0">
                    <IconStyle id="substyle_0">
                        <color>ff17d0fd</color>
                        <colorMode>normal</colorMode>
                        <scale>25.4</scale>
                        <heading>0</heading>
                        <Icon id="link_0">
                            <href>files/circle.png</href>
                        </Icon>
                    </IconStyle>
                </Style>
                <name>points</name>
                <open>0</open>
                <Placemark id="feat_4">
                    <description>
        &lt;table border=&quot;0&quot;&gt;
        &lt;tr&gt;&lt;td&gt;ID&lt;/td&gt;&lt;td&gt;355&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Time&lt;/td&gt;&lt;td&gt;2013-05-15 08:33:34+00:00&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Lon, Lat (&amp;deg;)&lt;/td&gt;&lt;td&gt;4.486, 52.412&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Altitude (m)&lt;/td&gt;&lt;td&gt;84&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Speed (m/s)&lt;/td&gt;&lt;td&gt;8.9&lt;/td&gt;&lt;/tr&gt;
        &lt;tr&gt;&lt;td&gt;Direction (&amp;deg;)&lt;/td&gt;&lt;td&gt;14.1&lt;/td&gt;&lt;/tr&gt;
        &lt;/table&gt;
        </description>
                    <TimeStamp id="time_0">
                        <when>2013-05-15T08:33:34+00:00</when>
                    </TimeStamp>
                    <styleUrl>#stylesel_0</styleUrl>
                    <Point id="geom_0">
                        <coordinates>4.485608,52.412252,84</coordinates>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                    </Point>
                </Placemark>
            </Folder>
            <Placemark id="feat_5">
                <styleUrl>#stylesel_1</styleUrl>
                <LineString id="geom_1">
                    <coordinates>4.485608,52.412252,0.0</coordinates>
                </LineString>
            </Placemark>
        </Folder>
    </Document>
</kml>
"""
        self.assertMultiLineEqual(kmlstr, expected)

