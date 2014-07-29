Ext.require(['Ext.ux.grid.FiltersFeature',
        'NLeSC.eEcology.form.field.TrackerSelector', 'Esc.ee.form.Panel']);

Ext.onReady(function() {
    Ext.QuickTips.init();

    Ext.create('Esc.ee.form.Panel', {
        items: [{
            xtype: 'trackergridselector',
            height: 300
        }]
    });
});
