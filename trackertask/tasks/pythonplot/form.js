Ext.require([
'Esc.ee.store.TrackerIds',
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
                 'leader',
                 {name: 'color', defaultValue: 'FF0000'},
                 {name: 'size', defaultValue: 'small'},
                 {name: 'speed', defaultValue: 4},
                 ]
    });

   var astore = new Ext.create('Esc.ee.store.TrackerIds', {
       model: 'Esc.eEcology.model.Tracker',
   });

   var available_trackers = {
       multiSelect: true,
       title            : 'Available',
       store            : astore,
       columns          : [{
           text: "ID", sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species'
       }, {
           text: "Project leader", flex: 1, sortable: true, dataIndex: 'leader'
       }],
   };

   var sstore = new Ext.create('Ext.data.Store', {
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
           text: "Project leader", flex: 1, sortable: true, dataIndex: 'leader',
           hidden: true
       }, {
           text: "Color", flex: 1, sortable: true, dataIndex: 'color',
           editor: {
               xtype: 'colorfield'
           },
           renderer: function(v, m) {
               m.style = 'cursor: pointer;background: #'+v;
               return v;
           }
       }, {
           text: "Size", flex: 1, sortable: true, dataIndex: 'size',
           editor: {
               xtype: 'combo',
               store: ['small', 'medium', 'large']
           }
       }, {
           text: "Speed class", flex: 1, sortable: true, dataIndex: 'speed',
           editor: {
               xtype: 'combo',
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
           columns: 2,
           items: [
               {
                   boxLabel  : '3D',
                   name      : 'alt',
                   inputValue: '3D',
                   checked: true
               }, {
                   boxLabel  : '2D',
                   name      : 'alt',
                   inputValue: '2D',
               }
           ]
       }, {
           xtype      : 'radiogroup',
           fieldLabel : 'Size',
           columns: 3,
           items: [{
                   boxLabel  : 'Small',
                   name      : 'size',
                   inputValue: 's',
                   id        : 'radio3'
            }, {
                   boxLabel  : 'Medium',
                   name      : 'size',
                   inputValue: 'm',
                   checked: true,
                   id        : 'radio1'
               }, {
                   boxLabel  : 'Large',
                   name      : 'size',
                   inputValue: 'l',
                   id        : 'radio2'
               }
           ]
       }, {
           xtype: 'trackergridselector',
           id: 'trackers',
//           buttons: ['add', 'remove'],
           fromGrid: available_trackers,
           toGrid: selected_trackers
       }]
   });
});
