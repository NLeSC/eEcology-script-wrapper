Ext.define('Esc.ee.form.field.DateTimeStart', {
    extend: 'Esc.ee.form.field.DateTime',
    alias: 'widget.xdatetimestart',
    fieldLabel: 'Start',
    name: 'start',
    value: new Date(new Date-(1000*60*60*24*3)), // today - 3 days
    allowBlank: false,
    itemId: 'startdt',
    vtype: 'daterange',
    endDateField: 'enddt' // id of the end date field
});
