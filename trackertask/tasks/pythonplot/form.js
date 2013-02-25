Ext.require([
             'Ext.grid.*',
             'Ext.data.*',
             'Ext.form.*',
             'Ext.dd.*',
             'Esc.ee.*'
         ]);

Ext.onReady(function() {
	Ext.QuickTips.init();

    Ext.define('Esc.eEcology.model.Tracker', {
        extend: 'Ext.data.Model',
        fields: ['id',
                 'species',
                 {name: 'color', defaultValue: 'red'},
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
           text: "ID", flex: 1, sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species'
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
           text: "Species", flex: 1, sortable: true, dataIndex: 'species'
           ,hidden: true
       }, {
           text: "Color", flex: 1, sortable: true, dataIndex: 'color',
           editor: {
               xtype: 'combo',
               store: colorlist,
               listConfig: {
                   getInnerTpl: function(displayField) {
                       return '<span style="background: {field1}">{field2}</span>';
                   }
               }
           },
           renderer: function(v, m) {
               m.style = 'cursor: pointer;background: '+v;
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
