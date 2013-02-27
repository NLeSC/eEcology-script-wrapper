Ext.require([
    'Esc.ee.store.TrackerIds',
    'Esc.ee.form.field.TrackerIdSelector',
    'Esc.ee.form.Panel'
]);

Ext.onReady(function() {
	Ext.QuickTips.init();

	var store = Ext.create('Esc.ee.store.TrackerIds');

	Ext.create('Esc.ee.form.Panel', {
       items: [{
    	   xtype: 'trackerselector',
    	   allowBlank: false,
    	   store: store,
    	   height: 300,
       }],
   });
});
