Ext.require([
    'Esc.ee.form.Panel',
    'NLeSC.form.field.DateTimeRange',
    'Esc.ee.store.TrackerIds',
    'Esc.ee.form.field.TrackerCombo',
]);

Ext.onReady(function() {
    Ext.QuickTips.init();

    var store = Ext.create('Esc.ee.store.TrackerIds');

    Ext.create('Esc.ee.form.Panel', {
       items: [{
           xtype: 'datetimerange'
       }, {
           xtype: 'trackercombo',
           store: store
       }, {xtype: 'displayfield', value:'Example 355 on 2010-06-28'}]
   });
});
