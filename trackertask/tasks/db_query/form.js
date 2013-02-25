Ext.onReady(function() {
	Ext.QuickTips.init();

	Ext.create('Esc.ee.form.Panel', {
       items: [{
    	   xtype: 'textarea',
    	   name: 'query',
    	   width: '100%',
    	   height: 300,
    	   value: 'SELECT device_info_serial FROM gps.uva_device_limited'
       }],
   });
});
