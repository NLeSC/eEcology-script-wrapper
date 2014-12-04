Ext.require(['Esc.ee.form.Panel', 'NLeSC.form.field.DateTimeRange',
        'NLeSC.eEcology.store.Trackers',
        'NLeSC.eEcology.form.field.TrackerCombo']);

Ext.onReady(function() {
    Ext.QuickTips.init();

    Ext.create('Esc.ee.form.Panel', {
        items: [{
            xtype: 'datetimerange'
        }, {
            xtype: 'trackercombo',
            name: 'tracker_id'
        }]
    });
});
