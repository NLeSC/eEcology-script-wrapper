Ext.require([
    'Esc.ee.form.Panel',
    'NLeSC.form.field.DateTimeRange',
    'Ext.ux.grid.FiltersFeature',
    'NLeSC.eEcology.store.Trackers',
    'NLeSC.eEcology.form.field.TrackerGrid',
    'Ext.form.field.Checkbox'
]);

Ext.onReady(function() {
    Ext.QuickTips.init();

    var tracker_store = Ext.create('NLeSC.eEcology.store.Trackers');
    tracker_store.load();

    Ext.create('Esc.ee.form.Panel', {
       items: [{
           xtype: 'datetimerange'
       }, {
           xtype: 'checkbox',
           name: 'plot_accel',
           checked: false,
           fieldLabel: 'Plot',
           boxLabel: 'Make accelerometer charts inside kml popup'
       }, {
           xtype: 'trackergridfield'
       }, {xtype: 'displayfield', value:'Example 355 on 2010-06-28'}]
   });
});
