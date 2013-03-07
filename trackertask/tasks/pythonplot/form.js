Ext.require([
    'Esc.ee.store.TrackerIds',
    'Esc.ee.form.Panel',
    'Esc.ee.form.field.DateTimeStart',
    'Esc.ee.form.field.DateTimeEnd',
    'Esc.ee.form.field.Color',
    'Esc.ee.form.field.TrackerGridSelector',
    'Esc.ee.store.Projects',
    'Esc.ee.store.Species',
    'Ext.grid.plugin.CellEditing',
    'Ext.ux.grid.FiltersFeature',
    'Ext.form.RadioGroup',
    'Ext.form.field.Radio'
]);

Ext.onReady(function() {
	Ext.QuickTips.init();

    Ext.define('Esc.eEcology.model.Tracker', {
        extend: 'Ext.data.Model',
        idProperty: 'id',
        fields: ['id',
                 'species',
                 'project',
                 {name: 'color', defaultValue: 'FF0000'},
                 {name: 'size', defaultValue: 'small'},
                 {name: 'speed', defaultValue: 4}
                 ]
    });

   var astore = Ext.create('Esc.ee.store.TrackerIds', {
       model: 'Esc.eEcology.model.Tracker'
   });

   var project_store = Ext.create('Esc.ee.store.Projects');

   var species_store = Ext.create('Esc.ee.store.Species');

   var available_trackers = {
       multiSelect: true,
       title            : 'Available',
       store            : astore,
       features         : [{
            ftype: 'filters',
            local: true
       }],
       columns          : [{
           text: "ID", sortable: true, dataIndex: 'id',
           filter: {type: 'numeric'}
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species',
           filter: {type: 'list', store: species_store}
       }, {
           text: "Project", flex: 1, sortable: true, dataIndex: 'project',
           filter: {type: 'list', store: project_store}
       }],
   };

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
               }, {
                   boxLabel  : 'Clamp to ground',
                   name      : 'alt',
                   inputValue: 'clampToGround',
               }, {
                   boxLabel  : 'Relative to ground',
                   name      : 'alt',
                   inputValue: 'relativeToGround',
                   checked: true
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
