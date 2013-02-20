Ext.require([
             'Ext.grid.*',
             'Ext.data.*',
             'Ext.form.*',
             'Ext.dd.*'
         ]);

Ext.onReady(function() {
	Ext.QuickTips.init();


   Ext.apply(Ext.form.field.VTypes, {
       daterange: function(val, field) {
           var date = val;

           if (!date) {
               return false;
           }
           if (field.startDateField && (!this.dateRangeMax || (date.getTime() != this.dateRangeMax.getTime()))) {
               var start = field.up('form').down('#' + field.startDateField);
               start.setMaxValue(date);
               this.dateRangeMax = date;
           }
           else if (field.endDateField && (!this.dateRangeMin || (date.getTime() != this.dateRangeMin.getTime()))) {
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
       daterangeText: 'Start date must be less than end date',
   });


	/**
	 * @class Ext.ux.form.field.DateTime
	 * @extends Ext.form.FieldContainer
	 * @author atian25 (http://www.sencha.com/forum/member.php?51682-atian25)
	 * @author ontho (http://www.sencha.com/forum/member.php?285806-ontho)
	 * @author jakob.ketterl (http://www.sencha.com/forum/member.php?25102-jakob.ketterl)
	 * @see http://www.sencha.com/forum/showthread.php?134345-Ext.ux.form.field.DateTime
	 */
	Ext.define('Ext.ux.form.field.DateTime', {
	    extend:'Ext.form.FieldContainer',
	    mixins:{
	        field:'Ext.form.field.Field'
	    },
	    alias: 'widget.xdatetime',

	    //configurables

	    combineErrors: false,
	    msgTarget: 'under',
	    layout: 'hbox',
	    readOnly: false,

	    /**
	     * @cfg {String} dateFormat
	     * The default is 'Y-m-d'
	     */
	    dateFormat: 'Y-m-d',
	    /**
	     * @cfg {String} timeFormat
	     * The default is 'H:i:s'
	     */
	    timeFormat: 'H:i:s',
	    /**
	     * @cfg {String} dateTimeFormat
	     * The format used when submitting the combined value.
	     * Defaults to 'Y-m-d H:i:s'
	     */
	    dateTimeFormat: 'Y-m-d H:i:s',
	    /**
	     * @cfg {Object} dateConfig
	     * Additional config options for the date field.
	     */
	    dateConfig:{},
	    /**
	     * @cfg {Object} timeConfig
	     * Additional config options for the time field.
	     */
	    timeConfig:{},


	    // properties

	    dateValue: null, // Holds the actual date
	    /**
	     * @property dateField
	     * @type Ext.form.field.Date
	     */
	    dateField: null,
	    /**
	     * @property timeField
	     * @type Ext.form.field.Time
	     */
	    timeField: null,

	    initComponent: function(){
	        var me = this;
	        me.items = me.items || [];

	        me.dateField = Ext.create('Ext.form.field.Date', Ext.apply({
	            format:me.dateFormat,
	            flex:1,
	            allowBlank: me.allowBlank,
	            reset: Ext.emptyFn,
	            submitValue:false
	        }, me.dateConfig));
	        me.items.push(me.dateField);

	        me.timeField = Ext.create('Ext.form.field.Time', Ext.apply({
	            format:me.timeFormat,
	            flex:1,
	            allowBlank: me.allowBlank,
	            reset: Ext.emptyFn,
	            submitValue:false
	        }, me.timeConfig));
	        me.items.push(me.timeField);

	        for (var i = 0; i < me.items.length; i++) {
	            me.items[i].on('focus', Ext.bind(me.onItemFocus, me));
	            me.items[i].on('blur', Ext.bind(me.onItemBlur, me));
	            me.items[i].on('specialkey', function(field, event){
	                var key = event.getKey(),
	                    tab = key == event.TAB;

	                if (tab && me.focussedItem == me.dateField) {
	                    event.stopEvent();
	                    me.timeField.focus();
	                    return;
	                }

	                me.fireEvent('specialkey', field, event);
	            });
	        }

	        me.callParent();

	        // this dummy is necessary because Ext.Editor will not check whether an inputEl is present or not
	        this.inputEl = {
	            dom:{},
	            swallowEvent:function(){}
	        };

	        me.initField();
	    },

	    focus:function(){
	        this.callParent();
	        this.dateField.focus();
	    },

	    onItemFocus:function(item){
	        if (this.blurTask) this.blurTask.cancel();
	        this.focussedItem = item;
	    },

	    onItemBlur:function(item){
	        var me = this;
	        if (item != me.focussedItem) return;
	        // 100ms to focus a new item that belongs to us, otherwise we will assume the user left the field
	        me.blurTask = new Ext.util.DelayedTask(function(){
	            me.fireEvent('blur', me);
	        });
	        me.blurTask.delay(100);
	    },

	    getValue: function(){
	        var value = null,
	            date = this.dateField.getSubmitValue(),
	            time = this.timeField.getSubmitValue();

	        if(date)
	        {
	            if(time)
	            {
	                var format = this.getFormat();
	                value = Ext.Date.parse(date + ' ' + time, format);
	            }
	            else
	            {
	                value = this.dateField.getValue();
	            }
	        }
	        return value;
	    },

	    getSubmitValue: function(){
	        var value = this.getValue();
	        return value ? Ext.Date.format(value, this.dateTimeFormat) : null;
	    },

	    setValue: function(value){
	        if (Ext.isString(value))
	        {
	            value = Ext.Date.parse(value, this.dateTimeFormat);
	        }
	        this.dateField.setValue(value);
	        this.timeField.setValue(value);
	    },

	    getFormat: function(){
	        return (this.dateField.submitFormat || this.dateField.format) + " " + (this.timeField.submitFormat || this.timeField.format);
	    },

	    // Bug? A field-mixin submits the data from getValue, not getSubmitValue
	    getSubmitData: function(){
	        var me = this,
	        data = null;
	        if (!me.disabled && me.submitValue && !me.isFileUpload()) {
	            data = {};
	            data[me.getName()] = '' + me.getSubmitValue();
	        }
	        return data;
	    },
	    setMaxValue: function(dt) {
	    	this.dateField.setMaxValue(dt);
	    },
	    setMinValue: function(dt) {
	    	this.dateField.setMinValue(dt);
	    },
	    getErrors: function(value) {
	    	var me = this;
	    	var errors = [];
	    	var vtype = me.vtype;
            var vtypes = Ext.form.field.VTypes;
	    	value = value || me.getValue();

	    	errors.concat(this.dateField.getErrors());
	    	errors.concat(this.timeField.getErrors());

	    	if (vtype) {
	            if(!vtypes[vtype](value, me)){
	                errors.push(me.vtypeText || vtypes[vtype +'Text']);
	            }
	        }
	    	return errors
	    }
	});

    Ext.define('Esc.eEcology.model.Tracker', {
        extend: 'Ext.data.Model',
        fields: ['id',
                 'species',
                 {name: 'color', defaultValue: 'red'}
                 ]
    });

    var colorlist = [
                     ["#0000FF"  , "Red"]
                     ,["#FF000"   , "Blue"]
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

   var astore = new Ext.create('Ext.data.Store', {
       model: 'Esc.eEcology.model.Tracker',
       proxy: {
           type: 'ajax',
           url : '../trackers.json',
           reader: {
        	   root: 'trackers',
               type: 'json'
           },
           writer: 'json'
       },
       autoLoad: true,
//           listeners: {
//               bulkremove: function(s, rs) {
//                   console.log(['bulkremove', rs]);
//               }
//           }
   });

   var available_trackers = Ext.create('Ext.grid.Panel', {
       multiSelect: true,
       viewConfig: {
           plugins: {
               ptype: 'gridviewdragdrop',
               dragGroup: 'firstGridDDGroup',
               dropGroup: 'secondGridDDGroup'
           },
       },
       store            : astore,
       columns          : [{
           text: "ID", flex: 1, sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species'
       }],
       stripeRows       : true,
       title            : 'Available',
       margins          : '0 2 0 0',
       listeners: {
    	   itemdblclick: function(t, r) {
               astore.remove([r]);
               sstore.add([r]);
    	   }
       }
   });

   var sstore = new Ext.create('Ext.data.Store', {
       model: 'Esc.eEcology.model.Tracker',
       getData: function() {
    	   return this.data.items.map(function(r) {
     		  return r.data;
     	   });
       }
//           listeners: {
//        	   add: function(s, rs) {
//        		   console.log(['Add', rs]);
//        	   }
//           }
   });

   var selected_trackers = Ext.create('Ext.grid.Panel', {
       viewConfig: {
           plugins: {
               ptype: 'gridviewdragdrop',
               dragGroup: 'secondGridDDGroup',
               dropGroup: 'firstGridDDGroup'
           },
       },
       store            : sstore,
       columns          : [{
           text: "ID", flex: 1, sortable: true, dataIndex: 'id'
       }, {
           text: "Species", flex: 1, sortable: true, dataIndex: 'species'
       }, {
           text: "Color", flex: 1, sortable: true, dataIndex: 'color',
           editor: {
               xtype: 'combo',
               store: colorlist
           },
           renderer: function(v, m) {
               m.style = 'background: '+v;
               return v;
           }
       }],
       selType: 'cellmodel',
       plugins: [
           Ext.create('Ext.grid.plugin.CellEditing', {
        	   triggerEvent: 'celldblclick',
        	   mode: 'MULTI',
        	   listeners: {
        		   beforeedit: function() {
        			   console.log('before edit');
        			   return true;
        		   }
        	   }
           })
       ],
       stripeRows       : true,
       title            : 'Selected',
       margins          : '0 2 0 0',
       listeners: {
           beforecelldblclick: function(t, td, i, r) {
        	   // only perform dblclick when color is selected
        	   if (selected_trackers.columns[i].text != 'Color') {
	        	   sstore.remove([r]);
	               astore.add([r]);
	               return false;
        	   }
        	   return true;
           },

       }
   });

   var form = Ext.create('Ext.form.Panel', {
       renderTo: 'form',
       width: 800,
       autoHeight: true,
       border: false,
       items: [{
    	   xtype: 'xdatetime',
    	   name: 'start',
           fieldLabel: 'Start',
    	   value: new Date(new Date-(1000*60*60*24*3)), // today - 3 days
           allowBlank: false,
           itemId: 'startdt',
           vtype: 'daterange',
           endDateField: 'enddt' // id of the end date field
       }, {
    	   xtype: 'xdatetime',
    	   name: 'end',
           fieldLabel: 'End',
    	   value: new Date(), // today
           allowBlank: false,
           itemId: 'enddt',
           vtype: 'daterange',
           startDateField: 'startdt' // id of the start date field
       }, {
           xtype      : 'radiogroup',
           fieldLabel : 'Altitude',
           columns: 2,
           items: [
               {
                   boxLabel  : '3D',
                   name      : 'alt',
                   inputValue: '3D',
                   checked: true
               }, {
                   boxLabel  : '2D',
                   name      : 'alt',
                   inputValue: '2D',
               }
           ]
       }, {
           xtype      : 'radiogroup',
           fieldLabel : 'Size',
           columns: 3,
           items: [{
                   boxLabel  : 'Small',
                   name      : 'size',
                   inputValue: 's',
                   id        : 'radio3'
            }, {
                   boxLabel  : 'Medium',
                   name      : 'size',
                   inputValue: 'm',
                   checked: true,
                   id        : 'radio1'
               }, {
                   boxLabel  : 'Large',
                   name      : 'size',
                   inputValue: 'l',
                   id        : 'radio2'
               }
           ]
       }, {
           xtype: 'panel',
           title: 'Trackers',
           layout: {
             type: 'hbox',
             align: 'stretch',
             padding: 5
           },
           autoWidth: true,
///           width        : 650,
           height       : 300,
           defaults     : { flex : 1 },
           items: [
             available_trackers,
             {
                 xtype: 'container',
                 flex: 0,
                 margins: '0 4',
                 layout: {
                     type: 'vbox',
                     pack: 'center'
                 },
                 defaults: {
                   xtype: 'button',
                   margin: '4 0 0 0'
                 },
                 items: [{
                     tooltip: 'Add to Selected',
                     text: '&rarr;',
                     handler: function() {
                         var records = available_trackers.getSelectionModel().getSelection();
                         astore.remove(records);
                         sstore.add(records);
                     }
                 }, {
                     tooltip: 'Remove from Selected',
                     text: '&larr;',
                     handler: function() {
                         var records = selected_trackers.getSelectionModel().getSelection();
                         sstore.remove(records);
                         astore.add(records);
                     }
                 }]
             },
             selected_trackers
           ]
       }],
       buttons: [{
           text: 'Submit',
           formBind: true,
           disabled: true,
           handler: function() {
               if (form.getForm().isValid()) {
            	   var data = form.getForm().getFieldValues();
            	   // add selected trackers store to form
            	   data['trackers'] = sstore.getData();

                   Ext.Ajax.request({
                       url: 'pythonplot',
                       method: 'POST',
                	   jsonData: data,
                       success: function(response, opts) {
                    	   var obj = Ext.decode(response.responseText);
                    	   // TODO ? change to polling for state.json route inside form
                    	   window.location = obj.state;
                       },
                       failure: function(response, opts) {
                           Ext.Msg.alert('Failed', response.status);
                       },
                   });
               }
           }
       }, {
           text: 'Reset',
           handler: function() {
        	   form.getForm().reset();
        	   sstore.removeAll();
        	   astore.load();
           }
       }]
   });
});
