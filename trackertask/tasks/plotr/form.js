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
        fields: ['id']
    });

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
   });

   var form = Ext.create('Ext.form.Panel', {
       renderTo: 'form',
       width: 800,
       autoHeight: true,
       border: false,
       items: [{
    	   xtype: 'xdatetimestart'
       }, {
    	   xtype: 'xdatetimeend'
       }, {
    	   xtype: 'combo',
    	   store: astore,
    	   name: 'id',
    	   displayField: 'id',
    	   valueField: 'id',
    	   allowBlank: false,
    	   fieldLabel: 'Tracker'
       }],
       buttons: [{
           text: 'Submit',
           formBind: true,
           disabled: true,
           handler: function() {
               if (form.getForm().isValid()) {
            	   var data = form.getForm().getFieldValues();

                   Ext.Ajax.request({
                       url: 'plotr',
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
