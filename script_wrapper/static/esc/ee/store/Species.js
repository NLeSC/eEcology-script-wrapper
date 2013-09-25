Ext.define('Esc.ee.store.Species', {
    extend: 'Ext.data.Store',
    fields: [
        {name: 'id', type: 'string'},
        {name: 'text', type: 'string'},
    ],
    proxy: {
        type: 'ajax',
        url : '../../species.json',
        reader: {
            type: 'json'
        }
    },
    sorters: [{
         property: 'id',
         direction: 'ASC'
    }],
    autoLoad: true
});
