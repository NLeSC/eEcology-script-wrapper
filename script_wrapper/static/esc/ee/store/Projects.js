Ext.define('Esc.ee.store.Projects', {
    extend: 'Ext.data.Store',
    fields: [
        {name: 'id', type: 'string'},
        {name: 'text', type: 'string'},
    ],
    proxy: {
        type: 'ajax',
        url : '../../projects.json',
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
