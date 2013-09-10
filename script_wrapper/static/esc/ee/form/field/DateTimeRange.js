/**
 * Combines Start and End Datetime fields
 */
Ext.define('Esc.ee.form.field.DateTimeRange', {
    extend: 'Ext.form.FieldContainer',
    requires: ['Esc.ee.form.field.DateTime'],
    alias: 'widget.datetimerange',
    layout: 'vbox',
    defaultType: 'xdatetime',
    defaults: {
        allowBlank: false
    },
    items: [{
        fieldLabel: 'Start',
        value: new Date(new Date-(1000*60*60*24*3)), // now - 3 days
        name: 'start'
    }, {
        fieldLabel: 'End',
        value: new Date(), // now
        name: 'end'
    }],
    getStartField: function() {
        return this.items.getAt(0);
    },
    getEndField: function() {
        return this.items.getAt(1);
    },
    afterComponentLayout: function() {
        var startField = this.getStartField();
        var endField = this.getEndField();

        this.setMinEnd(startField, startField.getValue());
        startField.on('change', this.setMinEnd, this);

        this.setMaxStart(endField, endField.getValue());
        endField.on('change', this.setMaxStart, this);
    },
    setMinEnd: function(startField, value) {
        var endField = this.getEndField();
        endField.setMinValue(value);
    },
    setMaxStart: function(endField, value) {
        var startField = this.getStartField();
        startField.setMaxValue(value);
    }
});