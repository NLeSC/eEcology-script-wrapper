Ext.onReady(function() {
	Ext.QuickTips.init();

	var form = Ext.create('Ext.form.Panel', {
       renderTo: 'form',
       width: 800,
       autoHeight: true,
       border: false,
    buttons: [{
        text: 'Submit',
        formBind: true,
        disabled: true,
        handler: function() {
            if (form.getForm().isValid()) {
         	   var data = form.getForm().getFieldValues();

                Ext.Ajax.request({
                    url: 'kmz_gen',
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
