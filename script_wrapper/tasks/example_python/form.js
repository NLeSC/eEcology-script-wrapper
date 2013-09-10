Ext.require([
    'Esc.ee.form.Panel',
    'Esc.ee.form.field.DateTimeRange',
    'Esc.ee.store.TrackerIds',
    'Esc.ee.form.field.TrackerIdSelector',
]);

Ext.onReady(function() {
    Ext.QuickTips.init();

    var store = Ext.create('Esc.ee.store.TrackerIds');

    Ext.create('Esc.ee.form.Panel', {
       items: [{
           xtype: 'datetimerange'
       }, {
           xtype: 'trackerselector',
           store: store
       }]
   });
});
