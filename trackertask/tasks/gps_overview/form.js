Ext.onReady(function() {
	Ext.QuickTips.init();

	var store = Ext.create('Esc.ee.store.TrackerIds');

	Ext.create('Esc.ee.form.Panel', {
       url: 'gps_overview',
       items: [{
    	   xtype: 'trackerselector',
    	   store: store,
    	   height: 300,
       }],
   });
});
