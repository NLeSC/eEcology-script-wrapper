var colorlist = [
    ["#0000FF"  , "Red"]
    ,["#FF0000"   , "Blue"]
    ,["#00FF00"  , "Green"]
    ,["#00FFFF"  , "Yellow"]
    ,["#FF00FF"  , "Purple"]
    ,["#FFFF00"  , "Aquamarine"]
    ,["red"  , "Red range"]
    ,["blue"   , "Blue range"]
    ,["green"  , "Green range"]
    ,["yellow"  , "Yellow range"]
    ,["purple"  , "Purple range"]
    ,["aquamarine"  , "Aquamarine range"]
];

/**
 * @author atian25 (http://www.sencha.com/forum/member.php?51682-atian25)
 * @author ontho (http://www.sencha.com/forum/member.php?285806-ontho)
 * @author jakob.ketterl (http://www.sencha.com/forum/member.php?25102-jakob.ketterl)
 * @author <a href="mailto:s.verhoeven@esciencecenter.nl">Stefan Verhoeven</a>
 * @see http://www.sencha.com/forum/showthread.php?134345-Ext.ux.form.field.DateTime
 */
Ext.define('Esc.ee.form.field.DateTime', {
	extend : 'Ext.form.FieldContainer',
	mixins : {
		field : 'Ext.form.field.Field'
	},
	requires: ['Ext.form.field.VTypes'],
	alias : 'widget.xdatetime',

	//configurables

	combineErrors : false,
	msgTarget : 'under',
	layout : 'hbox',
	readOnly : false,

	/**
	 * @cfg {String} dateFormat
	 * The default is 'Y-m-d'
	 */
	dateFormat : 'Y-m-d',
	/**
	 * @cfg {String} timeFormat
	 * The default is 'H:i:s'
	 */
	timeFormat : 'H:i:s',
	/**
	 * @cfg {String} dateTimeFormat
	 * The format used when submitting the combined value.
	 * Defaults to 'Y-m-d H:i:s'
	 */
	dateTimeFormat : 'Y-m-d H:i:s',
	labelAttrTpl : 'data-qtip="Format YYYY-MM-DD HH:MM:SS"',
	/**
	 * @cfg {Object} dateConfig
	 * Additional config options for the date field.
	 */
	dateConfig : {},
	/**
	 * @cfg {Object} timeConfig
	 * Additional config options for the time field.
	 */
	timeConfig : {},

	// properties

	dateValue : null, // Holds the actual date
	/**
	 * @property dateField
	 * @type Ext.form.field.Date
	 */
	dateField : null,
	/**
	 * @property timeField
	 * @type Ext.form.field.Time
	 */
	timeField : null,

	initComponent : function() {
		var me = this;
		me.items = me.items || [];

		me.dateField = Ext.create('Ext.form.field.Date', Ext
				.apply({
					format : me.dateFormat,
					flex : 1,
					allowBlank : me.allowBlank,
					reset : Ext.emptyFn,
					submitValue : false
				}, me.dateConfig));
		me.items.push(me.dateField);

		me.timeField = Ext.create('Ext.form.field.Time', Ext
				.apply({
					format : me.timeFormat,
					flex : 1,
					allowBlank : me.allowBlank,
					reset : Ext.emptyFn,
					submitValue : false
				}, me.timeConfig));
		me.items.push(me.timeField);

		for ( var i = 0; i < me.items.length; i++) {
			me.items[i].on('focus', Ext
					.bind(me.onItemFocus, me));
			me.items[i].on('blur', Ext.bind(me.onItemBlur, me));
			me.items[i]
					.on(
							'specialkey',
							function(field, event) {
								var key = event.getKey(), tab = key == event.TAB;

								if (tab
										&& me.focussedItem == me.dateField) {
									event.stopEvent();
									me.timeField.focus();
									return;
								}

								me.fireEvent('specialkey',
										field, event);
							});
		}

		Ext.apply(Ext.form.field.VTypes, {
		    daterange : function(val, field) {
		        var date = val;

		        if (!date) {
		            return false;
		        }
		        if (field.startDateField
		                && (!this.dateRangeMax || (date.getTime() != this.dateRangeMax
		                        .getTime()))) {
		            var start = field.up('form').down('#' + field.startDateField);
		            start.setMaxValue(date);
		            this.dateRangeMax = date;
		        } else if (field.endDateField
		                && (!this.dateRangeMin || (date.getTime() != this.dateRangeMin
		                        .getTime()))) {
		            var end = field.up('form').down('#' + field.endDateField);
		            end.setMinValue(date);
		            this.dateRangeMin = date;
		        }
		        /*
		         * Always return true since we're only using this vtype to set the
		         * min/max allowed values (these are tested for after the vtype test)
		         */
		        return true;
		    },
		    daterangeText : 'Start date must be less than end date',
		});

		me.callParent();

		// this dummy is necessary because Ext.Editor will not check whether an inputEl is present or not
		this.inputEl = {
			dom : {},
			swallowEvent : function() {
			}
		};

		me.initField();
	},

	focus : function() {
		this.callParent();
		this.dateField.focus();
	},

	onItemFocus : function(item) {
		if (this.blurTask)
			this.blurTask.cancel();
		this.focussedItem = item;
	},

	onItemBlur : function(item) {
		var me = this;
		if (item != me.focussedItem)
			return;
		// 100ms to focus a new item that belongs to us, otherwise we will assume the user left the field
		me.blurTask = new Ext.util.DelayedTask(function() {
			me.fireEvent('blur', me);
		});
		me.blurTask.delay(100);
	},

	getValue : function() {
		var value = null, date = this.dateField
				.getSubmitValue(), time = this.timeField
				.getSubmitValue();

		if (date) {
			if (time) {
				var format = this.getFormat();
				value = Ext.Date.parse(date + ' ' + time,
						format);
			} else {
				value = this.dateField.getValue();
			}
		}
		return value;
	},

	getSubmitValue : function() {
		var value = this.getValue();
		return value ? Ext.Date.format(value,
				this.dateTimeFormat) : null;
	},

	setValue : function(value) {
		if (Ext.isString(value)) {
			value = Ext.Date.parse(value, this.dateTimeFormat);
		}
		this.dateField.setValue(value);
		this.timeField.setValue(value);
	},

	getFormat : function() {
		return (this.dateField.submitFormat || this.dateField.format)
				+ " "
				+ (this.timeField.submitFormat || this.timeField.format);
	},

	// Bug? A field-mixin submits the data from getValue, not getSubmitValue
	getSubmitData : function() {
		var me = this, data = null;
		if (!me.disabled && me.submitValue
				&& !me.isFileUpload()) {
			data = {};
			data[me.getName()] = '' + me.getSubmitValue();
		}
		return data;
	},
	setMaxValue : function(dt) {
		this.dateField.setMaxValue(dt);
	},
	setMinValue : function(dt) {
		this.dateField.setMinValue(dt);
	},
	getErrors : function(value) {
		var me = this;
		var errors = [];
		var vtype = me.vtype;
		var vtypes = Ext.form.field.VTypes;
		value = value || me.getValue();

		errors.concat(this.dateField.getErrors());
		errors.concat(this.timeField.getErrors());

		if (vtype) {
			if (!vtypes[vtype](value, me)) {
				errors.push(me.vtypeText
						|| vtypes[vtype + 'Text']);
			}
		}
		return errors
	},
	listeners: {
	    afterRender: function() {
	        // BUG WORKAROUND for Uncaught TypeError: Object #<Object> has no method 'setStyle'
	        this.inputEl.setStyle = function() {};
	    }
	}
});

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

Ext.define('Esc.ee.store.TrackerIds', {
    extend: 'Ext.data.Store',
    fields: [{name: 'id', type: 'int'}],
    proxy: {
        type: 'ajax',
        url : '../../trackers.json',
        reader: {
            root: 'trackers',
            type: 'json'
        },
        writer: 'json'
    },
    sorters: [{
         property: 'id',
         direction: 'ASC'
    }],
    autoLoad: true
});

Ext.define('Esc.ee.form.TrackerCombo', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.trackercombo',
    displayField: 'id',
    allowBlank: false,
    fieldLabel: 'Tracker',
    labelAttrTpl : 'data-qtip="Tracker identifier aka device_info_serial"',
    name: 'id'
});

Ext.define('Esc.ee.form.TrackerIdSelector', {
    extend: 'Ext.ux.form.ItemSelector',
    alias: 'widget.trackerselector',
    name: 'trackers',
    fieldLabel: 'Trackers',
    labelAttrTpl : 'data-qtip="Tracker identifiers aka device_info_serial"',
    imagePath: 'http://cdn.sencha.com/ext/beta/4.2.0.489/examples/images/',
    displayField: 'id',
    valueField: 'id',
    allowBlank: false,
    fromTitle: 'Available',
    toTitle: 'Selected'
});

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
    width: 800,
    autoHeight: true,
    border: false,
    jsonSubmit: true,
    requires: [
        'Ext.data.Store',
        'Ext.window.Window',
        'Ext.grid.Panel',
        'Ext.window.MessageBox'
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
                }]
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

Ext.define('Esc.ee.form.TrackerGridSelector', {
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

