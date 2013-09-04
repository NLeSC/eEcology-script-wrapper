Ext.require([
    'Esc.ee.form.Panel',
    'Esc.ee.form.field.DateTimeStart',
    'Esc.ee.form.field.DateTimeEnd',
    'Esc.ee.form.field.Color',
    'Esc.ee.form.field.TrackerGridSelector',
    'Ext.grid.plugin.CellEditing',
    'Ext.form.RadioGroup',
    'Ext.form.field.Radio'
]);

Ext.onReady(function() {
    Ext.QuickTips.init();

    Ext.define('Esc.eEcology.model.Tracker', {
        extend: 'Ext.data.Model',
        fields: ['id',
                 'species',
                 'project',
                 {name: 'color', defaultValue: 'FFFF50'},
                 {name: 'size', defaultValue: 'small'},
                 {name: 'speed', defaultValue: 4},
                 ]
    });

   var sstore = Ext.create('Ext.data.Store', {
       model: 'Esc.eEcology.model.Tracker'
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
       }, {
           text: "Size", flex: 1, sortable: true, dataIndex: 'size',
           editor: {
               xtype: 'combo',
               forceSelection: true,
               store: ['small', 'medium', 'large']
           }
       }, {
           text: "Speed class", flex: 1, sortable: true, dataIndex: 'speed',
           editor: {
               xtype: 'combo',
               forceSelection: true,
               store: [1,2,3,4]
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
           xtype: 'xdatetimestart'
       }, {
           xtype: 'xdatetimeend'
       }, {
           xtype      : 'radiogroup',
           fieldLabel : 'Altitude',
           columns: 3,
           items: [
               {
                   boxLabel  : 'Absolute',
                   name      : 'alt',
                   inputValue: 'absolute',
                   checked: true
               }, {
                   boxLabel  : 'Clamp to ground',
                   name      : 'alt',
                   inputValue: 'clampToGround'
               }, {
                   boxLabel  : 'Relative to ground',
                   name      : 'alt',
                   inputValue: 'relativeToGround'
               }
           ]
       }, {
           xtype: 'trackergridselector',
           id: 'trackers',
           buttons: ['add', 'remove'],
           toGrid: selected_trackers
       }]
   });
});
