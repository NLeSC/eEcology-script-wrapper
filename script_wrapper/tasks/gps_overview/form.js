Ext.require(['Ext.ux.grid.FiltersFeature',
        'NLeSC.eEcology.form.field.TrackerSelector', 'Esc.ee.form.Panel']);

Ext.onReady(function() {
    Ext.QuickTips.init();

    var tracker_store = Ext.create('NLeSC.eEcology.store.Trackers');
    tracker_store.load();

    Ext.create('Esc.ee.form.Panel', {
        items: [{
            xtype: 'trackergridselector',
            height: 300
        }]
    });
});
