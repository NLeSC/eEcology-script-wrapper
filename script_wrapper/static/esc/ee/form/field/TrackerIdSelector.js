/**
 * Available and selected multi select list of tracker identifiers.
 * Tracker identifiers can be drag/drop, move buttons or double clicked to swap between selected and available.
 *
 * On submission will return a array of selected tracker identifiers.
 */
Ext.define('Esc.ee.form.field.TrackerIdSelector', {
    extend: 'Ext.ux.form.ItemSelector',
    alias: 'widget.trackerselector',
    name: 'trackers',
    fieldLabel: 'Trackers',
    labelAttrTpl : 'data-qtip="Tracker identifiers aka device_info_serial"',
    imagePath: 'http://cdn.sencha.com/ext/beta/4.2.0.489/examples/images/',
    displayField: 'id',
    valueField: 'id',
    allowBlank: false,
    msgTarget: 'under',
    fromTitle: 'Available',
    toTitle: 'Selected'
});
