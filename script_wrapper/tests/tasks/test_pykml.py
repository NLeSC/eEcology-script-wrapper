from datetime import datetime
import unittest
import pkgutil
from mock import patch
from colander.iso8601 import UTC
from colander import Invalid
import simplekml
import simplekml.featgeom
import simplekml.timeprimitive
import simplekml.substyle
import simplekml.styleselector
from script_wrapper.tasks.pykml import PyKML


class TestPyKML(unittest.TestCase):

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

    def assertKml(self, testname, kml):
        expected = pkgutil.get_data('script_wrapper.tests.data', testname + '.kml')
        self.assertMultiLineEqual(kml.kml(), expected)

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
        formfields = {'start': '2013-05-14T10:11:12Z',
                      'end': '2013-05-15T08:33:34Z',
                      'trackers': [{'id': 1234, 'color': color}],
                      'shape': 'circle',
                      'size': 'medium',
                      'colorby': 'ispeed',
                      'speedthreshold1': 5,
                      'speedthreshold2': 10,
                      'speedthreshold3': 20,
                      'transparency': 0,
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
                     'start': '2013-05-14T10:11:12Z',
                     'end': '2013-05-15T08:33:34Z',
                     'trackers': [{'id': 1234, 'color': ecolor}],
                     'shape': 'circle',
                     'size': 'medium',
                     'sizebyalt': False,
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
        formfields = {'start': '2013-05-14T10:11:12Z',
                      'end': '2013-05-15T08:33:34Z',
                      'trackers': [{'id': 1234, 'color': color}],
                      # wrong shape
                      'shape': 'square',
                      'size': 'medium',
                      'colorby': 'ispeed',
                      'speedthreshold1': 5,
                      'speedthreshold2': 10,
                      'speedthreshold3': 20,
                      'transparency': 100,
                      'altitudemode': 'absolute',
                      }
        db_url = 'postgresql://localhost/eecology'
        with self.assertRaises(Invalid) as e:
            task.formfields2taskargs(formfields, db_url)

        expected = {'shape': u'"square" is not one of circle, iarrow, tarrow'
                    }
        self.assertEqual(e.exception.asdict(), expected)

    def test_addIcons2kml_circlepngarrowpngadded(self):
        kml = simplekml.Kml()
        task = PyKML()

        path = task.addIcons2kml(kml)

        self.assertIn('files/arrow.png', path)
        self.assertIn('files/circle.png', path)

    def test_trackrows2kml_2pointswithdefaultstyle(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 8.91, 14.1, 14.2,
                 4.0,
                 ],
                [355, datetime(2013, 5, 15, 8, 34, 34, tzinfo=UTC),
                 4.485608, 52.415252, 34,
                 8.90, 9.91, 14.1, 14.2,
                 3.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('2pointswithdefaultstyle', kml)

    def test_trackrows2kml_singlepointwithdefaultstyle(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('singlepointwithdefaultstyle', kml)

    def test_trackrows2kml_negativealt_clamped(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, -5,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('negativealt', kml)

    def test_trackrows2kml_speedzero_slowestcolor(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 0.0, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('speedzero', kml)

    def test_trackrows2kml_halftransparent(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('halftransparent', kml)

    def test_trackrows2kml_fixedcolor_fastcolor(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('fixedcolor', kml)

    def test_trackrows2kml_shapeiarrow_arrowwithheadingasicon(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'iarrow',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('shapeiarrow', kml)

    def test_trackrows2kml_shapetarrow_arrowwithheadingasicon(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'tarrow',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('shapetarrow', kml)

    def test_trackrows2kml_fastestspeed_fastestcolor(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 28.90, 29.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('fastestspeed', kml)

    def test_trackrows2kml_fastspeed_fastcolor(self):

        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 13.90, 19.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('fastspeed', kml)

    def test_trackrows2kml_slowestspeed_slowestcolor(self):
        self.maxDiff = None
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 0.13, 0.19, 29.91, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
                 'colorby': 'ispeed',
                 'speedthresholds': [0.5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absolute',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#EEFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        self.assertKml('slowestspeed', kml)        

    def test_trackrows2kml_sizebyalton_iconsizebig(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': True,
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

        self.assertKml('sizebyalton', kml)

    def test_trackrows2kml_sizebyaltonlargesize_iconsizebig(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'large',
                 'sizebyalt': True,
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

        self.assertKml('sizebyaltonlargesize', kml)

    def test_trackrows2kml_sizebyaltonsmallsize_iconsizebig(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'small',
                 'sizebyalt': True,
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

        self.assertKml('sizebyaltonsmallsize', kml)

    def test_altituderelativebyground(self):
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 9.91, 14.1, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'relativeToGround',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        self.assertKml('altituderelativebyground', kml)

    def test_trackrows2kml_idirectionnoneispeednone(self):
        self.maxDiff = None
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 None, 9.91, None, 14.2,
                 4.0,
                 ],
                ]
        style = {'shape': 'iarrow',
                 'size': 'medium',
                 'sizebyalt': False,
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

        self.assertKml('directionnone', kml)
        
    def test_trackrows2kml_absoluteClampBelowGround(self):
        self.maxDiff = None
        kml = simplekml.Kml()
        task = PyKML()
        rows = [[355, datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                 4.485608, 52.412252, 84,
                 8.90, 8.91, 14.1, 14.2,
                 50,
                 ],
                [355, datetime(2013, 5, 15, 8, 34, 34, tzinfo=UTC),
                 4.485608, 52.415252, 34,
                 8.90, 9.91, 14.1, 14.2,
                 50,
                 ],
                ]
        style = {'shape': 'circle',
                 'size': 'medium',
                 'sizebyalt': False,
                 'colorby': 'ispeed',
                 'speedthresholds': [5, 10, 20],
                 'alpha': 100,
                 'altitudemode': 'absoluteClampBelowGround',
                 }
        tracker = {'id': 355,
                   'color': {'slowest': '#FFFF50',
                             'slow': '#FDD017',
                             'fast': '#C68E17',
                             'fastest': '#733C00'
                             }
                   }

        task.trackrows2kml(kml, rows, tracker, style)

        self.assertKml('absoluteclampbelowground', kml)
