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

    var tracker_store = Ext.create('NLeSC.eEcology.store.Trackers');
    tracker_store.load();

    Ext.define('ColoredTracker', {
        extend: 'NLeSC.eEcology.model.Tracker',
        fields: [{
            name: 'color',
            defaultValue: 'FFFF50'
        }, {
            name: 'size',
            defaultValue: 'small'
        }, {
            name: 'speed',
            defaultValue: 4
        }]
    });

    var colors = ['FFFF50', 'F7E8AA', 'FFA550', '5A5AFF', 'BEFFFF', '8CFF8C',
            'FF8CFF', 'AADD96', 'FFD3AA', 'C6C699', 'E5BFC6', 'DADADA',
            'C6B5C4', 'C1D1BF', '000000'];

    var sstore = Ext.create('Ext.data.Store', {
        model: 'ColoredTracker',
        listeners: {
            add: function(s, records) {
                // Cycle through colors when selecting a tracker
                records.forEach(function(record) {
                    if (!('color' in record.data)) {
                        record.set('color',
                                colors[record.index % colors.length]);
                    }
                });
            }
        }
    });

   var selected_trackers = {
       title            : 'Selected',
       store            : sstore,
       columns          : [{
           text: "ID", flex: 1, sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species',
           hidden: true
       }, {
           text: "Project", flex: 1, sortable: true, dataIndex: 'project',
           hidden: true
       }, {
           text: "Base color", flex: 1, sortable: true, dataIndex: 'color',
           editor: {
               xtype: 'colorfield',
               pickerCls: 'color-picker16',
               colors: [
                'FFFF50',
                'F7E8AA',
                'FFA550',
                '5A5AFF',
                'BEFFFF',
                '8CFF8C',
                'FF8CFF',
                'AADD96',
                'FFD3AA',
                'C6C699',
                'E5BFC6',
                'DADADA',
                'C6B5C4',
                'C1D1BF',
                '000000'
               ]
           },
           renderer: function(v, m) {
               m.style = 'cursor: pointer;background: #'+v;
               return v;
           }
       }],
       multiSelect: false, // Editing is weird with multiselect=true
       plugins: [
           Ext.create('Ext.grid.plugin.CellEditing', {
               triggerEvent: 'cellclick'
           })
       ],
       viewConfig: {
           markDirty: false
       }
   };

   var form = Ext.create('Esc.ee.form.Panel', {
       id:'myform',
       items: [{
           xtype: 'datetimerange'
       }, {
           xtype: 'radiogroup',
           fieldLabel: 'Icon shape',
           columns: 2,
           items: [{
               boxLabel: 'Circle', name: 'icon', inputValue: 'circle', checked: true
           }, {
               boxLabel: 'Direction arrow', name: 'icon', inputValue: 'arrow'
           }]
       }, {
           xtype: 'trackergridselector',
           id: 'trackers',
           buttons: ['add', 'remove'],
           toGrid: selected_trackers
       }, {
           xtype: 'displayfield',
           value: 'Click on base color grid cell to change color of tracker.'
       }]
   });
});
