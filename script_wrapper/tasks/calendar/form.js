Ext.require([
    'Esc.ee.form.Panel',
    'NLeSC.form.field.DateTimeRange',
    'Ext.ux.grid.FiltersFeature',
    'NLeSC.eEcology.store.Trackers',
    'NLeSC.eEcology.form.field.TrackerGrid'
]);

Ext.onReady(function() {
    Ext.QuickTips.init();

    Ext.create('Esc.ee.form.Panel', {
       items: [{
           xtype: 'datetimerange'
       }, {
           xtype: 'trackergridfield'
       }]
   });
});
