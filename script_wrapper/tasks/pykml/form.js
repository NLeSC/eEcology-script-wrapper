Ext.require([
    'Esc.ee.form.Panel',
    'NLeSC.form.field.DateTimeRange',
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
