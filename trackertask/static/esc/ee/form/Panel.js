/**
 * @author <a href="mailto:s.verhoeven@esciencecenter.nl">Stefan Verhoeven</a>
 *
 * Form which can save the form values by user supplied name and restore form values later.
 *
 */
Ext.define('Esc.ee.form.Panel', {
    extend: 'Ext.form.Panel',
    url: '.',
    renderTo: 'form',
    width: 911,
    autoHeight: true,
    border: false,
    jsonSubmit: true,
    requires: [
        'Ext.data.Store',
        'Ext.window.Window',
        'Ext.grid.Panel',
        'Ext.window.MessageBox',
        'Ext.data.proxy.LocalStorage',
        'Ext.grid.column.Action'
    ],
    initComponent : function() {
        var me = this;
        this.callParent();

        this.persistentStore = Ext.create('Ext.data.Store', {
            fields: ['name', 'query'],
            proxy: {
                type: 'localstorage',
                // Each task should have it own selection storage
                // Each task has it's own path so use that as selection storage identifier
                id: window.location.pathname
            },
            autoLoad: true,
            listeners: {
                datachanged: function(store) {
                    var isEmpty = store.count() == 0;
                    me.down('button[action=load]').setDisabled(isEmpty);
                    if (isEmpty) me.persistentGrid.hide();
                }
            }
        });

        this.persistentGrid = Ext.create('Ext.window.Window', {
            title: 'Saved selections',
            closeAction: 'hide',
            layout: 'fit',
            width: 400,
            height: 200,
            items: {
                xtype: 'grid',
                store: this.persistentStore,
                columns: [{
                    text: 'Name', dataIndex: 'name', flex:1
                }, {
                    xtype: 'actioncolumn', width: 50,
                    items: [{
                        iconCls: 'icon-load',
                        tooltip: 'Load',
                        handler: function(grid, rowIndex, colIndex) {
                            var rec = grid.getStore().getAt(rowIndex);
                            var form = me.getForm();
                            var values = Ext.JSON.decode(rec.data.query);
                            form.setValues(values);
                            this.up('window').hide();
                        }
                    }, {
                        iconCls: 'icon-delete',
                        tooltip: 'Delete',
                        handler: function(grid, rowIndex, colIndex) {
                            var rec = grid.getStore().getAt(rowIndex);
                            rec.destroy();
                        }
                    }]
                }],
                listeners: {
                    itemdblclick: function(grid, rec) {
                        var form = me.getForm();
                        var values = Ext.JSON.decode(rec.data.query);
                        form.setValues(values);
                        this.up('window').hide();
                    }
                }
            }
        });
    },
    buttons: [{
        text: 'Save selection',
        formBind: true,
        disabled: true,
        handler: function() {
            var form = this.up('form');
            Ext.Msg.prompt('Save selection', 'Name:', function(btn, name) {
                var query = Ext.JSON.encode(form.getForm().getFieldValues());
                form.persistentStore.add({'name': name, 'query': query});
                form.persistentStore.sync();
            }, form, false, Ext.Date.format(new Date(), 'c'));
        }
    }, {
        disabled: true,
        action: 'load',
        text: 'Restore saved selection',
        handler: function() {
            var form = this.up('form');
            form.persistentStore.load();
            form.persistentGrid.show();
        }
    }, {
        text: 'Reset',
        handler: function() {
            var form = this.up('form').getForm();
            form.reset();
        }
    }, {
        text: 'Submit',
        formBind: true,
        disabled: true,
        handler: function() {
            var form = this.up('form').getForm();
            if (form.isValid()) {
                form.submit({
                    success: function(f, action) {
                      var obj = Ext.decode(action.response.responseText);
                        // TODO ? change to polling for state.json route inside form
                      window.location = obj.state;
                    },
                    failure: function(response, opts) {
                        Ext.Msg.alert('Failed', response.status);
                    },
                });
            }
        }
    }]
});
