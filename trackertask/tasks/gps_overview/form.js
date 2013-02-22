Ext.require([
             'Ext.grid.*',
             'Ext.data.*',
             'Ext.form.*',
             'Ext.dd.*'
         ]);

Ext.onReady(function() {
	Ext.QuickTips.init();

	Ext.define('Esc.eEcology.model.Tracker', {
        extend: 'Ext.data.Model',
        fields: ['id',
                 'species',
                 {name: 'color', defaultValue: 'red'}
                 ]
    });

    var colorlist = [
                     ["#0000FF"  , "Red"]
                     ,["#FF000"   , "Blue"]
                     ,["#00FF00"  , "Green"]
                     ,["#00FFFF"  , "Yellow"]
                     ,["#FF00FF"  , "Purple"]
                     ,["#FFFF00"  , "Aquamarine"]
                     ,["red"  , "Red range"]
                     ,["blue"   , "Blue range"]
                     ,["green"  , "Green range"]
                     ,["yellow"  , "Yellow range"]
                     ,["purple"  , "Purple range"]
                     ,["aquamarine"  , "Aquamarine range"]
                   ];

   var astore = new Ext.create('Ext.data.Store', {
       model: 'Esc.eEcology.model.Tracker',
       proxy: {
           type: 'ajax',
           url : '../trackers.json',
           reader: {
        	   root: 'trackers',
               type: 'json'
           },
           writer: 'json'
       },
       sorters: [{
    	    property: 'id',
    	    direction: 'ASC'
       }],
       autoLoad: true,
//           listeners: {
//               bulkremove: function(s, rs) {
//                   console.log(['bulkremove', rs]);
//               }
//           }
   });

   var available_trackers = Ext.create('Ext.grid.Panel', {
       multiSelect: true,
       viewConfig: {
           plugins: {
               ptype: 'gridviewdragdrop',
               dragGroup: 'firstGridDDGroup',
               dropGroup: 'secondGridDDGroup'
           },
       },
       store            : astore,
       columns          : [{
           text: "ID", flex: 1, sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species'
       }],
       stripeRows       : true,
       title            : 'Available',
       margins          : '0 2 0 0',
       listeners: {
    	   itemdblclick: function(t, r) {
               astore.remove([r]);
               sstore.add([r]);
    	   }
       }
   });

   var sstore = new Ext.create('Ext.data.Store', {
       model: 'Esc.eEcology.model.Tracker',
       getData: function() {
    	   return this.data.items.map(function(r) {
     		  return r.data;
     	   });
       },
       sorters: [{
   	     property: 'id',
   	     direction: 'ASC'
       }]
//           listeners: {
//        	   add: function(s, rs) {
//        		   console.log(['Add', rs]);
//        	   }
//           }
   });

   var selected_trackers = Ext.create('Ext.grid.Panel', {
       viewConfig: {
           plugins: {
               ptype: 'gridviewdragdrop',
               dragGroup: 'secondGridDDGroup',
               dropGroup: 'firstGridDDGroup'
           },
       },
       store            : sstore,
       columns          : [{
           text: "ID", flex: 1, sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species'
       }, {
           text: "Color", flex: 1, sortable: true, dataIndex: 'color',
           editor: {
               xtype: 'combo',
               store: colorlist
           },
           renderer: function(v, m) {
               m.style = 'background: '+v;
               return v;
           }
       }],
       selType: 'cellmodel',
       plugins: [
           Ext.create('Ext.grid.plugin.CellEditing', {
        	   triggerEvent: 'celldblclick',
        	   mode: 'MULTI',
        	   listeners: {
        		   beforeedit: function() {
        			   console.log('before edit');
        			   return true;
        		   }
        	   }
           })
       ],
       stripeRows       : true,
       title            : 'Selected',
       margins          : '0 2 0 0',
       listeners: {
           beforecelldblclick: function(t, td, i, r) {
        	   // only perform dblclick when color is selected
        	   if (selected_trackers.columns[i].text != 'Color') {
	        	   sstore.remove([r]);
	               astore.add([r]);
	               return false;
        	   }
        	   return true;
           },

       }
   });

   var form = Ext.create('Ext.form.Panel', {
       renderTo: 'form',
       width: 800,
       autoHeight: true,
       border: false,
       items: [{
           xtype: 'panel',
           title: 'Trackers',
           layout: {
             type: 'hbox',
             align: 'stretch',
             padding: 5
           },
           autoWidth: true,
///           width        : 650,
           height       : 300,
           defaults     : { flex : 1 },
           items: [
             available_trackers,
             {
                 xtype: 'container',
                 flex: 0,
                 margins: '0 4',
                 layout: {
                     type: 'vbox',
                     pack: 'center'
                 },
                 defaults: {
                   xtype: 'button',
                   margin: '4 0 0 0'
                 },
                 items: [{
                     tooltip: 'Add to Selected',
                     text: '&rarr;',
                     handler: function() {
                         var records = available_trackers.getSelectionModel().getSelection();
                         astore.remove(records);
                         sstore.add(records);
                     }
                 }, {
                     tooltip: 'Remove from Selected',
                     text: '&larr;',
                     handler: function() {
                         var records = selected_trackers.getSelectionModel().getSelection();
                         sstore.remove(records);
                         astore.add(records);
                     }
                 }]
             },
             selected_trackers
           ]
       }],
       buttons: [{
           text: 'Submit',
           formBind: true,
           disabled: true,
           handler: function() {
               if (form.getForm().isValid()) {
            	   var data = form.getForm().getFieldValues();
            	   // add selected trackers store to form
            	   data['trackers'] = sstore.getData();

                   Ext.Ajax.request({
                       url: 'gps_overview',
                       method: 'POST',
                	   jsonData: data,
                       success: function(response, opts) {
                    	   var obj = Ext.decode(response.responseText);
                    	   // TODO ? change to polling for state.json route inside form
                    	   window.location = obj.state;
                       },
                       failure: function(response, opts) {
                           Ext.Msg.alert('Failed', response.status);
                       },
                   });
               }
           }
       }, {
           text: 'Reset',
           handler: function() {
        	   form.getForm().reset();
        	   sstore.removeAll();
        	   astore.load();
           }
       }]
   });
});
