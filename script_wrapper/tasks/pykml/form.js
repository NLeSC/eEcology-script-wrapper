Ext.require([
    'Esc.ee.form.Panel',
    'NLeSC.form.field.DateTimeRange',
    'NLeSC.eEcology.form.field.Color',
    'Ext.ux.grid.FiltersFeature',
    'NLeSC.eEcology.form.field.TrackerSelector',
    'Ext.grid.plugin.CellEditing',
    'Ext.form.RadioGroup',
    'Ext.form.field.Radio'
]);

Ext.onReady(function() {
    Ext.QuickTips.init();

    Ext.define('ColorScheme', {
        extend: 'Ext.data.Model',
        fields: [{name: 'id', type: 'int'}, 'slowest', 'slow', 'fast', 'fastest']
    });

    Ext.define('ColoredTracker', {
        extend: 'NLeSC.eEcology.model.Tracker',
        fields: [{
            name: 'colorid', type: 'int'
        }, {
            name: 'color'
        }]
    });

    var colorschemes = Ext.create('Ext.data.ArrayStore', {
        model: 'ColorScheme',
        data: [
            [1, '#FFFF50', '#FDD017', '#C68E17', '#733C00'], // OK GEEL -DONKERGEEL
            [2, '#F7E8AA', '#F9E070', '#FCB514', '#A37F14'], // OK GEEL -GEELGROEN
            [3, '#FFA550', '#EB4100', '#FF0000', '#7D0000'], // OK ORANJE ROOD
            [4, '#5A5AFF', '#0000FF', '#0000AF', '#00004B'], // OK FEL BLAUW
            [5, '#BEFFFF', '#00FFFF', '#00B9B9', '#007373'], // OK LICHT BLAUW
            [6, '#8CFF8C', '#00FF00', '#00B900', '#004B00'], //  FEL GROEN
            [7, '#FF8CFF', '#FF00FF', '#A500A5', '#4B004B'], //  OK PAARS
            [8, '#AADD96', '#60C659', '#339E35', '#3A7728'], // OK GROEN
            [9, '#FFD3AA', '#F9BA82', '#F28411', '#BF5B00'], // OK
            [10, '#C6C699', '#AAAD75', '#6B702B', '#424716'], // OK
            [11, '#E5BFC6', '#D39EAF', '#A05175', '#7F284F'], // OK  ROZE-PAARS
            [12, '#DADADA', '#C3C3C3', '#999999', '#3C3C3C'], //  VAN WIT NAAR DONKERGRIJS
            [13, '#C6B5C4', '#A893AD', '#664975', '#472B59'], // OK BLAUWPAARS
            [14, '#C1D1BF', '#7FA08C', '#5B8772', '#21543F'], // OK GRIJSGROEN
//            [15, '#000000', '#000000', 'rgba(0,0,0, 0,5)', 'rgb(0,0,0,0.05)'], // BLACK
            ]
    });

    var editicon = '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAH8SURBVDjLjZPfS1NhGMdXf0VEQhDUhdCN4X0IYT8ghIJQM0KoC4vushZddLELKyRhQQkSFIKEGEkUCI2oxVhepG5zi1xbc0u3cDs7Z+ec/ezT+x62scmmHvhwDrzP93Pe57znsQE2cR0SdAm6d+GwYL/M1LBVBV35fF4plUqVcrlMK8Q6TqdzYrukJuiW4Vwuh67rdbLZLJlMhmQyaUnigVlC05f4+dbB0tQplp92DsnwPimQBaZpUigUrLtE0zQURSGVSqHF37DhGkVZeQdagszKLJ7HvZtNAhmuIQWGYaCqKps/ZkivPqCwPs/Gp0cYvjnKUTe+F9fMJoFoo96zfJZ9K+sLpP33qRhujPANtr7dJPhqmO/PBxX3+PljTYLtqImPpH13qZge9LUrmLEB1FU7sZd9jJw5MljNthYk/KLnxdFqeAjzdz9Z/z3Ck2fRE36qx9pakAjME1y4Lbb9GTMyTD52GUXsZO3ZadTkL6umrSD4ZZrAezvLH54Q915EjwywtXSH8FQf+t+I9V12FLwe6wE1SmjyAi77Qb6Kt3rGe9H+hKzwrgLH9eMUPE4K3gm8jpPMjRwlHfNTLBbr7Cjo7znA2NVOXA/PsThzi2wyah1pI+0E/9rNQQsqMtM4CyfE36fLhb2ERa0mB7BR0CElexjnGnL0O2T2PyFunSz8jchwAAAAAElFTkSuQmCC" data-qtip="Click to change color"/>';
    var colorSchemeTpl = Ext.create('Ext.XTemplate',
    '<table><tr><td style="background:{slowest};width: 30px"></td><td style="background:{slow};width: 30px;"></td><td style="background:{fast};width: 30px;"></td><td style="background:{fastest};width: 30px;"></td><td>',editicon,'</td></tr></table>'
    );

    var colorSchemeComboTpl = Ext.create('Ext.XTemplate',
    '<tpl for=".">',
    '<div class="x-boundlist-item">',
    '<table><tr><td style="background:{slowest};width: 30px;">&nbsp;</td><td style="background:{slow};width: 30px;">&nbsp;</td><td style="background:{fast};width: 30px;">&nbsp;</td><td style="background:{fastest};width: 30px;">&nbsp;</td></tr></table>',
    '</div>',
    '</tpl>');

    var colorTpl = Ext.create('Ext.XTemplate', '<table><tr><td style="background:{fast};width: 120px;">&nbsp;</td><td>', editicon, '</td></tr></table>');
    var colorComboTpl = Ext.create('Ext.XTemplate', '<tpl for=".">', '<div class="x-boundlist-item">', '<table><tr><td style="background:{fast};width: 120px;">&nbsp;</td></td></table>', '</div>', '</tpl>');

    Ext.define('My.ColorSchemePicker', {
        extend: 'Ext.form.ComboBox',
        alias: 'widget.mycolorschemepicker',
        store: colorschemes,
        queryMode: 'local',
        displayField: 'fast',
        valueField: 'id',
        tpl: colorSchemeComboTpl,
        // wanted to use html as display, but html is not allowed, so using the middle color
        displayTpl: Ext.create('Ext.XTemplate', '<tpl for=".">{fast}</tpl>'),
        listeners: {
            select: function (combo, record, index) {
                var color = record[0].data.fast;
                combo.inputEl.setStyle('background', color);
            }
        }
    });

    var mycolorschemerenderer = function (v, m, r) {
        m.style = 'cursor: pointer;';
        var html = colorSchemeTpl.apply(r.data.color);
        return html;
    };

    Ext.define('My.ColorPicker', {
        extend: 'Ext.form.ComboBox',
        alias: 'widget.mycolorpicker',
        store: colorschemes,
        queryMode: 'local',
        displayField: 'fast',
        valueField: 'id',
        tpl: colorComboTpl,
        // wanted to use html as display, but html is not allowed, so using the middle color
        displayTpl: Ext.create('Ext.XTemplate', '<tpl for=".">{fast}</tpl>'),
        listeners: {
            select: function (combo, record, index) {
                var color = record[0].data.fast;
                combo.inputEl.setStyle('background', color);
            },
            focus: function(combo) {
              combo.expand();
            }
        }
    });

    var mycolorrenderer = function (v, m, r) {
        m.style = 'cursor: pointer;';
        var html = colorTpl.apply(r.data.color);
        return html;
    };

    var sstore = Ext.create('Ext.data.Store', {
        model: 'ColoredTracker',
        listeners: {
            add: function(store, records) {
                // Cycle through colors when selecting a tracker
                records.forEach(function(record) {
                	var idx = store.indexOf(record);
                    if (!('color' in record.data)) {
                    	var next_color = colorschemes.getAt(idx % colorschemes.getCount());
                        record.set(
                            'color',
                            next_color.data
                        );
                        record.set(
                    		'colorid',
                    		next_color.data.id
                        );
                        record.commit();
                    }
                });
            }
        }
    });

    var editing = Ext.create('Ext.grid.plugin.CellEditing', {
        triggerEvent: 'cellclick'
    });

    var getSelectedTrackersGrid = function() {
        return Ext.ComponentMgr.get('selected_trackers');
    };

    var getColorColumn = function() {
        var sgrid = getSelectedTrackersGrid();
        var color_column = sgrid.columns.filter(function(d) {return d.dataIndex === 'colorid';})[0];
        return color_column;
    };

    var selected_trackers = {
       title: 'Selected',
       store: sstore,
       id: 'selected_trackers',
       columns: [{
           text: "ID", flex: 1, sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species',
           hidden: true
       }, {
           text: "Project", flex: 1, sortable: true, dataIndex: 'project',
           hidden: true
       }, {
           text: "Color", flex: 1, sortable: true, dataIndex: 'colorid',
           editor: {
               xtype: 'mycolorschemepicker'
           },
           renderer: mycolorschemerenderer
       }],
       multiSelect: false, // Editing is weird with multiselect=true
       plugins: [editing],
       listeners: {
            edit: function(editor, e) {
                if (e.field == 'colorid') {
                    var color = colorschemes.getById(e.value);
                    e.record.set('color', color.data);
                }
                // commit the changes right after editing finished
                e.record.commit();
            }
       }
   };

   var form = Ext.create('Esc.ee.form.Panel', {
       id:'myform',
       items: [{
           xtype: 'datetimerange',
           layout: 'hbox',
           defaults: {
             margin: '0 10 0 0'
           }
       }, {
           xtype: 'radiogroup',
           fieldLabel: 'Shape',
           columns: 3,
           items: [{
               boxLabel: 'Circle', name: 'shape', inputValue: 'circle', checked: true
           }, {
               boxLabel: 'Instantaneous directional arrow', name: 'shape', inputValue: 'iarrow'
           }, {
               boxLabel: 'Traject directional arrow', name: 'shape', inputValue: 'tarrow', disabled: true
           }]
       }, {
    	   xtype: 'radiogroup',
    	   fieldLabel: 'Size',
         columns: 3,
    	   items: [{
    		   boxLabel: 'Small', name: 'size', inputValue: 'small'
    	   }, {
    		   boxLabel: 'Medium', name: 'size', inputValue: 'medium', checked: true, fieldStyle: 'font-size: 140%;'
    	   }, {
    		   boxLabel: 'Large', name: 'size', inputValue: 'large', fieldStyle: 'font-size: 170%;'
    	   }]
       }, {
    	   xtype: 'checkbox',
    	   fieldLabel: 'Size based on altitude',
    	   name: 'sizebyalt'
       }, {
    	   xtype: 'radiogroup',
    	   fieldLabel: 'Color based on',
         columns: 3,
    	   items: [{
    		   boxLabel: 'One color for each tracker', name: 'colorby', inputValue: 'fixed'
    	   }, {
    		   boxLabel: 'Instantaneous speed', name: 'colorby', inputValue: 'ispeed', checked: true
    	   }, {
    		   boxLabel: 'Traject speed', name: 'colorby', inputValue: 'tspeed', disabled: true
    	   }],
    	   listeners: {
    		   change: function(field, value) {
    			   var colorby = value.colorby;
    			   var use_color_scheme = colorby === 'ispeed' || colorby === 'tspeed';
				   field.up('form').down('#speedthresholds').setDisabled(!use_color_scheme);
				   var color_column = getColorColumn();
				   if (use_color_scheme) {
				       color_column.setEditor(Ext.create('My.ColorSchemePicker'));
				       color_column.renderer = mycolorschemerenderer;
				   } else {
                       color_column.setEditor(Ext.create('My.ColorPicker'));
				       color_column.renderer = mycolorrenderer;
				   }
				   // trigger column redraw
				   getSelectedTrackersGrid().view.refresh();
    		   }
    	   }
       }, {
    	   xtype: 'fieldcontainer',
    	   id: 'speedthresholds',
    	   fieldLabel: 'Speed thresholds (m/s)',
    	   layout: {
               type: 'hbox',
               defaultMargins: {top: 0, right: 5, bottom: 0, left: 0}
           },
    	   items: [{
    		   xtype: 'displayfield', value:'Slowest', fieldStyle: 'background: #FFFFE6', submitValue: false
    	   }, {
    		   xtype: 'numberfield', name: 'speedthreshold1', value: 5, minValue: 0, maxValue: 100, width: 50
    	   }, {
    		   xtype: 'displayfield', value:'Slow', fieldStyle: 'background: #FFFFB2', submitValue: false
    	   }, {
    		   xtype: 'numberfield', name: 'speedthreshold2', value: 10, minValue: 0, maxValue: 100, width: 50
    	   }, {
    		   xtype: 'displayfield', value:'Fast', fieldStyle: 'background: #FFFF33', submitValue: false
    	   }, {
    		   xtype: 'numberfield', name: 'speedthreshold3', value: 20, minValue: 0, maxValue: 100, width: 50
    	   }, {
    		   xtype: 'displayfield', value:'Fastest', fieldStyle: 'background:	#CCCC00', submitValue: false
    	   }]
       }, {
    	   xtype: 'numberfield',
    	   fieldLabel: 'Transparency (%)',
    	   labelAttrTpl:'data-qtip="100% is fully opaque, 0% is fully transparent"',
    	   name: 'alpha',
    	   width: 155,
    	   value: 100,
    	   minValue: 0,
    	   maxValue: 100
       }, {
           xtype: 'radiogroup',
           fieldLabel: 'Altitude',
           columns: 3,
           items: [{
               boxLabel: 'Absolute',
               name: 'altitudemode',
               inputValue: 'absolute',
               checked: true
           }, {
               boxLabel: 'Clamp to ground',
               name: 'altitudemode',
               inputValue: 'clampToGround'
           }, {
               boxLabel: 'Relative to ground',
               name: 'altitudemode',
               inputValue: 'relativeToGround',
               disabled: true
           }]
       }, {
           xtype: 'trackergridselector',
           buttons: ['add', 'remove'],
           toGrid: selected_trackers
       }, {
           xtype: 'displayfield',
           submitValue: false,
           value: 'Click on base color grid cell to change color of tracker.'
       }]
   });
});
