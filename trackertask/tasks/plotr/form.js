Ext.require([
    'Esc.ee.store.TrackerIds',
    'Esc.ee.form.Panel',
    'Esc.ee.form.field.DateTimeStart',
    'Esc.ee.form.field.DateTimeEnd',
    'Esc.ee.form.field.TrackerCombo',
]);

Ext.onReady(function() {
	Ext.QuickTips.init();

	var store = Ext.create('Esc.ee.store.TrackerIds');

	var form = Ext.create('Esc.ee.form.Panel', {
        items: [{
        	xtype: 'xdatetimestart'
        }, {
        	xtype: 'xdatetimeend'
        }, {
    	    xtype: 'trackercombo',
    	    store: store
       }]
   });
});
