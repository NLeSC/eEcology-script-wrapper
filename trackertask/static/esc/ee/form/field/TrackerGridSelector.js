Ext.define('Esc.ee.form.field.TrackerGridSelector', {
    extend: 'Ext.form.FieldContainer',
    alias: 'widget.trackergridselector',
    fieldLabel: 'Trackers',
    name: 'trackers',
    labelAttrTpl : 'data-qtip="Selected tracker identifiers with additional data"',
    mixins: {
        field: 'Ext.form.field.Field'
    },
    requires: [
        'Ext.button.Button',
    ],
    uses: ['Ext.grid.plugin.DragDrop'],
    /**
     * @cfg {Object} fromGrid (required)
     * Grid config object used as from Grid.
     */

    /**
     * @cfg {Object} toGrid (required)
     * Grid config object used as to Grid.
     */

    /**
     * @cfg String [dragText="{0} Item{1}"] The text to show while dragging items.
     * {0} will be replaced by the number of items. {1} will be replaced by the plural
     * form if there is more than 1 item.
     */
    dragText: '{0} Tracker{1}',
    /**
     * @cfg {Boolean} [hideNavIcons=false] True to hide the navigation icons
     */
    hideNavIcons:false,
    /**
     * @cfg {Array} buttons Defines the set of buttons that should be displayed in between the ItemSelector
     * fields. Defaults to <tt>['top', 'up', 'add', 'remove', 'down', 'bottom']</tt>. These names are used
     * to build the button CSS class names, and to look up the button text labels in {@link #buttonsText}.
     * This can be overridden with a custom Array to change which buttons are displayed or their order.
     */
    buttons: ['top', 'up', 'add', 'remove', 'down', 'bottom'],

    /**
     * @cfg {Object} buttonsText The tooltips for the {@link #buttons}.
     * Labels for buttons.
     */
    buttonsText: {
        top: "Move to Top",
        up: "Move Up",
        add: "Add to Selected",
        remove: "Remove from Selected",
        down: "Move Down",
        bottom: "Move to Bottom"
    },
    defaults     : { flex : 1 },
    layout: {
        type: 'hbox',
        align: 'stretch'
    },
    initComponent: function() {
        var me = this;

        me.ddGroup = me.id + '-dd';
        me.callParent();
    },
    autoWidth: true,
    height: 300,
    defaults: { flex : 1 },
    initComponent: function() {
        var me = this;
        me.items = me.setupItems();
        me.callParent();
        me.initField();
    },
    createList: function(grid) {
        var me = this;

        grid.disabled = me.disabled;
        grid.margins = '0 2 0 0';

        if (!grid.viewConfig) {
            grid.viewConfig = {}
        }
        if (!grid.viewConfig.plugins) {
            grid.viewConfig.plugins = []
        }
        if (Ext.isObject(grid.viewConfig.plugins)) {
            grid.viewConfig.plugins = [grid.viewConfig.plugins]
        }
        grid.viewConfig.plugins.push({
            ptype: 'gridviewdragdrop',
            ddGroup: me.ddGroup,
            dragText: me.dragText
        });

        var field = Ext.create('Ext.grid.Panel', grid);
        field.addListener('itemdblclick', me.onItemDblClick, me);

        return field;
    },
    createButtons: function() {
        var me = this,
        buttons = [];

        if (!me.hideNavIcons) {
            Ext.Array.forEach(me.buttons, function(name) {
                buttons.push({
                    xtype: 'button',
                    tooltip: me.buttonsText[name],
                    handler: me['on' + Ext.String.capitalize(name) + 'BtnClick'],
                    cls: Ext.baseCSSPrefix + 'form-itemselector-btn',
                    iconCls: Ext.baseCSSPrefix + 'form-itemselector-' + name,
                    navBtn: true,
                    scope: me,
                    margin: '4 0 0 0'
                });
            });
        }
        return buttons;
    },
    setupItems: function() {
        var me = this;

        me.ddGroup = 'TrackerGridSelectorDD-'+Ext.id()

        me.fromField = me.createList(me.fromGrid);
        me.toField = me.createList(me.toGrid);

        return [
            me.fromField,
            {
                xtype: 'container',
                margins: '0 4',
                flex: 0,
                layout: {
                    type: 'vbox',
                    pack: 'center'
                },
                items: me.createButtons()
            },
            me.toField
        ];
    },
    /**
     * Get the selected records from the specified list.
     *
     * Records will be returned *in store order*, not in order of selection.
     * @param {Ext.grid.Panel} list The list to read selections from.
     * @return {Ext.data.Model[]} The selected records in store order.
     *
     */
    getSelections: function(list) {
        var store = list.getStore();

        return Ext.Array.sort(list.getSelectionModel().getSelection(), function(a, b) {
            a = store.indexOf(a);
            b = store.indexOf(b);

            if (a < b) {
                return -1;
            } else if (a > b) {
                return 1;
            }
            return 0;
        });
    },

    onTopBtnClick : function() {
        var list = this.toField,
            store = list.getStore(),
            selected = this.getSelections(list);

        store.suspendEvents();
        store.remove(selected, true);
        store.insert(0, selected);
        store.resumeEvents();
        list.getSelectionModel().select(selected);
    },

    onBottomBtnClick : function() {
        var list = this.toField,
            store = list.getStore(),
            selected = this.getSelections(list);

        store.suspendEvents();
        store.remove(selected, true);
        store.add(selected);
        store.resumeEvents();
        list.getSelectionModel().select(selected);
    },

    onUpBtnClick : function() {
        var list = this.toField,
            store = list.getStore(),
            selected = this.getSelections(list),
            rec,
            i = 0,
            len = selected.length,
            index = 0;

        // Move each selection up by one place if possible
        store.suspendEvents();
        for (; i < len; ++i, index++) {
            rec = selected[i];
            index = Math.max(index, store.indexOf(rec) - 1);
            store.remove(rec, true);
            store.insert(index, rec);
        }
        store.resumeEvents();
        list.getSelectionModel().select(selected);
    },

    onDownBtnClick : function() {
        var list = this.toField,
            store = list.getStore(),
            selected = this.getSelections(list),
            rec,
            i = selected.length - 1,
            index = store.getCount() - 1;

        // Move each selection down by one place if possible
        store.suspendEvents();
        for (; i > -1; --i, index--) {
            rec = selected[i];
            index = Math.min(index, store.indexOf(rec) + 1);
            store.remove(rec, true);
            store.insert(index, rec);
        }
        store.resumeEvents();
        list.getSelectionModel().select(selected);
    },

    onAddBtnClick : function() {
        var me = this,
            selected = me.getSelections(me.fromField);

        me.moveRec(true, selected);
        me.toField.getSelectionModel().select(selected);
    },

    onRemoveBtnClick : function() {
        var me = this,
            selected = me.getSelections(me.toField);

        me.moveRec(false, selected);
        me.fromField.getSelectionModel().select(selected);
    },

    moveRec: function(add, recs) {
        var me = this,
            fromField = me.fromField,
            toField   = me.toField,
            fromStore = add ? fromField.store : toField.store,
            toStore   = add ? toField.store   : fromField.store;

//        fromStore.suspendEvents();
//        toStore.suspendEvents();
        fromStore.remove(recs);
        toStore.add(recs);
//        fromStore.resumeEvents();
//        toStore.resumeEvents();
    },

    onItemDblClick: function(view, rec) {
        this.moveRec(view === this.fromField.getView(), rec);
    },

    setValue: function(value) {
        console.log('Setting value');
    },

    onBindStore: function(store, initial) {
        var me = this;

        if (me.fromField) {
            me.fromField.store.removeAll()
            me.toField.store.removeAll();

            // Add everything to the from field as soon as the Store is loaded
            if (store.getCount()) {
                me.populateFromStore(store);
            } else {
                me.store.on('load', me.populateFromStore, me);
            }
        }
    },

    populateFromStore: function(store) {
        var fromStore = this.fromField.store;

        // Flag set when the fromStore has been loaded
        this.fromStorePopulated = true;

        fromStore.add(store.getRange());

        // setValue waits for the from Store to be loaded
        fromStore.fireEvent('load', fromStore);
    },

    onEnable: function(){
        var me = this;

        me.callParent();
        me.fromField.enable();
        me.toField.enable();

        Ext.Array.forEach(me.query('[navBtn]'), function(btn){
            btn.enable();
        });
    },

    onDisable: function(){
        var me = this;

        me.callParent();
        me.fromField.disable();
        me.toField.disable();

        Ext.Array.forEach(me.query('[navBtn]'), function(btn){
            btn.disable();
        });
    },

    onDestroy: function(){
        this.bindStore(null);
        this.callParent();
    },
    setupValue: function(value){
        return value.map(function(r) {
            return r.data;
        });
    },
    getValue: function(){
        return this.setupValue(this.toField.store.data.items) || [];
    },
    /**
     * Returns the value that would be included in a standard form submit for this field.
     *
     * @return {String} The value to be submitted, or `null`.
     */
    getSubmitValue: function() {
        return Ext.JSON.encode(this.getValue());
    },
});

