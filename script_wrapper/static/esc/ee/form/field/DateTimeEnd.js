Ext.define('Esc.ee.form.field.DateTimeEnd', {
    extend: 'Esc.ee.form.field.DateTime',
    alias: 'widget.xdatetimeend',
    name: 'end',
    fieldLabel: 'End',
    value: new Date(), // today
    allowBlank: false,
    itemId: 'enddt',
    vtype: 'daterange',
    startDateField: 'startdt' // id of the start date field
});
