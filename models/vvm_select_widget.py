# coding: utf8

'''

    ***  VVMSelectWidget - OPTIONS chain widget for web2py  ***
    *** Created by Vadim V. Mostovoy, vadim *at* routix.net ***
    
    INSTALLATION:
        - just place file "vvm_select_widget.py" into "models" folder;
          now you can create widget instances in your controllers!
    
    DESCRIPTION:
        - creates dependent OPTIONS chain (cascade);
        - integrated "select-or-add-new" functionality (ajax + jQuery-ui dialog);
        - can be used as "select-or-add-new" for a single not cascaded dropdown list;
        - works in both cases, record creation and record updating;
        - adjustable or default fields representation (formats);
        - adjustable or default placeholders;
        - it is up to you, for which dropdown to show "Add..." links;
        - uses default validators, css, etc.;
        - self-sufficient, no additional views, controllers, models needed;
        - multiple widgets per page allowed;
        - you can provide you own javascript dropdown-change event handler
          to react on select/deselect event;
        - secure (there is no way to create fake request with substituted tables/fields
            to attack your application; only specified tables can be changed);
          
    NOTES:
        - uses jQuery and jQuery-ui javascript libraries;
          default "layout.html" imports those libraries into your aplication by default;
          if you use customized views which do not import jQuery libraries, you must 
          load those libraries explicitly into your view before using this widget;

    EXAMPLE MODELS:
    
        db.define_table('Kind',
            Field('Name', length=50, unique=True, required=True, notnull=True, label="Product kind"),
            format='%(Name)s')

        db.define_table('Category',
            Field('Kind_id', db.Kind, required=True, notnull=True, label="Kind"),
            Field('Name', length=50, required=True, notnull=True, label="Category name"),
            format='%(Name)s')

        db.define_table('Subcategory',
            Field('Category_id', db.Category, required=True, notnull=True, label="Category"),
            Field('Name', length=50, required=True, notnull=True, label="Subcategory name"),
            format='%(Name)s')
            
        db.define_table('Product',
            Field('Subcategory_id', db.Subcategory, required=True, notnull=True, label="Product group"),
            Field('Name', length=100, required=True, notnull=True),
            format='%(Name)s')
    
    EXAMPLES:

    # =================================================

    # 1. Simple way
    
        # define tables hierarchy
        sel_widget = VVMSelectWidget(db.Kind, db.Category, db.Subcategory)
        
        # set widget, note: you must set widget to field with "set_widget_to()" method!
        sel_widget.set_widget_to(db.Product.Subcategory_id)
        
        return dict(crud=crud.create(db.Product))
        # or:
        #return dict(crud=crud.update(db.Product, 13))

    # =================================================

    # 2. More configurable way
    
        # fields formats/representations; if all or some omited - default formats
        # will be used; Formats can be either strings or functions
        formats = dict(Kind="%(Name)s", Category="%(Name)s", Subcategory=lambda row: "%(Name)s (%(id)s)" % row)
        
        # placeholder used when selected nothing; if omited - default will be used
        # can be either string or function
        placeholder = lambda table: "Select %s..." % str(table).lower()
        
        # define fields for which we will show "Add..." links
        # Note: db.Kind is omited; This means that user cannot add new records to db.Kind
        add_links_to = [db.Category, db.Subcategory]
        
        # width for dialog; if omited - sizes will be ajusted automatically
         dialog_width=500
         dialog_height=300
    
        # create widget instance
        sel_widget = VVMSelectWidget(db.Kind, db.Category, db.Subcategory, 
                     placeholder=placeholder, 
                     formats=formats,
                     dialog_width=dialog_width,
                     dialog_height-dialog_height,
                     add_links_to=add_links_to,
                     dialog_width=dialog_width)
                   
        sel_widget.set_widget_to(db.Product.Subcategory_id)
        
        return dict(crud=crud.create(db.Product))
        
    # =================================================
    
    # 3. If you need just "Add..." link next to your single dropdown,
    # but not cascading your dropdowns - just omit tables 
    # hierarchy list in the constructor!
    
        # create class without tables hierarchy
        # in this case widget will add link for
        # a new record creation and nothing more
        sel_widget = VVMSelectWidget()
        
        sel_widget.set_widget_to(db.Product.Subcategory_id)
        
        return dict(crud=crud.create(db.Product))
    
    # =================================================
    
    # 4. Sometimes you need to show/hide other page elements as a result
    # of dropdown select/deselect event; in this case you can supply
    # your own event handler to widget; here is an example of dropdown
    # color changing; color value depends on dropdown value
    
    # NOTE: be careful; poorly written javascript event handler can
    # halt execution of other javascript code on your page! use
    # exception catching in your event handler; in any case your
    # javascript code must not raise any exceptions and must have
    # correct javascript syntax

        # define javascript event handler
        change_handler_js = """

            function(dropdown) {
                if ($(dropdown).val() > 0)
                    $(dropdown).css("background-color", "#EBF5CC");
                else
                    $(dropdown).css("background-color", "#FFE6E6");
            }
            
        """
    
        # define tables hierarchy and set your js event handler
        sel_widget = VVMSelectWidget(db.Kind, db.Category, db.Subcategory,
            change_handler_js=change_handler_js)
        
        # set widget
        sel_widget.set_widget_to(db.Product.Subcategory_id)
        
        return dict(crud=crud.create(db.Product))
        
    # =================================================
    
'''

class VVMSelectWidget(object):
    
    def __init__(self, *tables, **named):
        self._uid = None
        self._db = None
        self._wuid = "VVM_Options_widget"
        self._tables = tables
        self._named = named

    def is_addition_allowed(self, table):
        if not self._tables:
            return True
        else:
            return (self._named and ("add_links_to" in self._named) and
                   (table in self._named["add_links_to"]))

    def get_widget_attributes(self, field, widget, **attributes):
        attr = dict(
            _id = '%s_%s' % (field._tablename, field.name),
            _class = "generic-widget",
            _name = field.name,
            requires = field.requires,
            )
        attr.update(widget)
        attr.update(attributes)
        return attr

    def get_ref_names(self, field):
        if not field or not field.type.startswith('reference'):
            return (None, None)
        else:
            referenced = field.type[10:].strip()
            if (referenced.find('.') > -1):
                return referenced.split('.')
            else:
                return (referenced, "id")

    def get_ref_field(self, table):
        parent = None
        for t in self._tables:
            if t._tablename == table._tablename:
                break
            parent = t
        if parent:
            for f in table:
                rtname, rfname = self.get_ref_names(f)
                if rtname == parent._tablename:
                    return f
        return None

    def str_to_field(self, full_field_name):
        if (not full_field_name) or not ("." in full_field_name):
            return None
        t, f = full_field_name.split(".")
        t = self._db[t] if (t in self._db) else None
        if not t:
            return None
        f = t[f] if (f in t) else None
        return f
        
    def field_to_ref(self, field):
        if not field:
            return None
        f = self.str_to_field(field) if isinstance(field, str) else field
        if not f.type.startswith('reference'):
            return None
        referenced = f.type[10:].strip()
        if (referenced.find('.') == -1):
            referenced = referenced + ".id"
        return self.str_to_field(referenced)

    def get_chain(self, field, including_this=True, is_reversed=False):
        res = []
        if field and including_this:
            res.append(field)
        ref = self.field_to_ref(field)
        if not ref:
            return res
        ref = self.get_ref_field(ref._table)
        start_found = False
        for t in reversed(self._tables):
            if not ref:
                break
            if not start_found:
                start_found = ref._table == t
            if not start_found:
                continue
            if ref._table != t:
                break
            res.append(ref)
            ref = self.field_to_ref(ref)
            if ref:
                ref = self.get_ref_field(ref._table)
        if not is_reversed:
            res.reverse()
        return res;
            
    def repr(self, fmt, data):
        import types
        if isinstance(fmt, types.FunctionType):
            return str(fmt(data))
        else:
            return str(fmt % data)

    def get_options(self, field, value, parent, parent_id, inner_items_only=False):
        default = dict(value=value)
        attr = self.get_widget_attributes(field, default)
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()
            else:
                raise SyntaxError, 'widget cannot determine options of %s' % field
        opts = []
        for (k, v) in options:
            if (not k and not v):
                rtname, rfname = self.get_ref_names(field)
                if self._named and ("placeholder" in self._named):
                    placeholder = self.repr(self._named["placeholder"], self._db[rtname])
                else:
                    placeholder = "%s..." % rtname
                opt = OPTION(placeholder, _value="0")
            else:
                row = parent._table(k) if parent else None
                ref_id = row[parent.name] if row else None
                if self._named and ("formats" in self._named):
                    formats = self._named["formats"]
                    rtname, rfname = self.get_ref_names(field)
                    if rtname in formats:
                        fmt = formats[rtname]
                        if fmt:
                            row = self._db[rtname](k)
                            v = self.repr(fmt, row) if row else v
                opt = OPTION(v, _value=k, _reference=ref_id)
            opts.append(opt)

        sel = SELECT(*opts, _parent_id=parent_id, **attr)

        if inner_items_only:
            items = "<!-- items -->\n"
            for opt in sel:
                items += opt.xml() + "\n"
            return items
        else:
            return sel

    def set_widget_to(self, field):
        self._uid = "%s_%s_%s" % (self._wuid, field._tablename, field.name)
        self._db = field._db
        field.widget = self.widget_internal
        #shared_js_url = "%s?%s_action=sharedScript.js" % (request.url, self._wuid)
        #if not shared_js_url in response.files:
        #    response.files.append(shared_js_url);
        self.ajax_check(field)
    
    def widget_internal(self, f, v):
        self.ajax_check(f)
        extension = []
        chain = self.get_chain(f)        
        parent = None
        widget_id = None
        parent_id = ""
        
        if self._named and ("dialog_width" in self._named):
            dialog_width = self._named["dialog_width"]
        else:
            dialog_width = 0
        if self._named and ("dialog_height" in self._named):
            dialog_height = self._named["dialog_height"]
        else:
            dialog_height = 0

        for link in chain:
            val = v if link == f else 0
            widget = self.get_options(link, val, parent, widget_id)
            widget_id = widget.attributes.get('_id', None)
            ext = []
            div = DIV(_id="%s_div" % widget_id)
            ref = self.field_to_ref(link)
            if self.is_addition_allowed(ref.table):
                add_link = SPAN(XML("&nbsp;&nbsp;"), A("Add...", \
                        _href="javascript:showAddDialog('%s', '%s', {'dlg_name':'%s_dlg', 'target':'%s', 'parent':'%s', 'dialog_width':%s, 'dialog_height':%s});" % \
                        (self._uid, request.url, widget_id, str(link), parent_id, dialog_width, dialog_height)),
                        _tied_to=widget_id, _class="span_add_link")
                ext.append(add_link)
            ext.insert(0, widget)
            div.components.extend(ext)
            extension.append(div)
            parent = link
            parent_id = widget_id

        container_div = DIV(_id=self._uid)
        
        if self._named and ("change_handler_js" in self._named):
            change_handler_js = self._named["change_handler_js"]
        else:
            change_handler_js = "null"
        extension.append(self.get_widget_js(uid=self._uid, change_handler_js=change_handler_js, shared_code=self.get_shared_js()))

        container_div.components.extend(extension)
        return container_div

    def ajax_check(self, f):

        if request.get_vars:
            get_action = request.get_vars[self._wuid + "_action"]
            if get_action == "sharedScript.js":
                raise HTTP(200, 
                           self.get_shared_js(),
                           **{"Content-Type": "text/javascript"})
        
        if not request.post_vars:
            return
        uid = request.post_vars[self._uid + "_widget"]
        if (uid != self._uid):
            return
        op = request.post_vars[self._uid + "_operation"]
        if not (op in ["ajax_dialog_submit", "ajax_dialog_content"]):
            return
        dlg = request.post_vars[self._uid + "_dialog"]
        trg = request.post_vars[self._uid + "_target"]
        if not trg:
            return
        if not self.is_addition_allowed(self.field_to_ref(trg)._table):
            raise HTTP(403)
        
        parent_value = request.post_vars[self._uid + "_parent_value"]
        forms = {}
        chain = self.get_chain(f)

        for link in chain:
            link.default = parent_value
            ref = self.field_to_ref(link)
            form = SQLFORM(ref._table).process()

            if form.accepted:
                parent = self.get_ref_field(ref._table)
                parent_name = "%s_%s" % (parent._tablename, parent.name) if parent else None
                items = self.get_options(link, form.vars.id, parent, parent_name, True)
                raise HTTP(200, items)
            elif form.errors:
                raise HTTP(200, form)
                
            forms[link._tablename] = form

        if (op == "ajax_dialog_content"):        
            fld = self.str_to_field(trg)
            if not fld:
                raise HTTP(400)

            raise HTTP(200, forms[fld._tablename])

    def get_shared_js(self, **args):
        return '''

            function checkErrorVisibility(dropdown) {
                var parentDivId = "div#" + $(dropdown).attr("id") + "_div";
                $(parentDivId + " [class='error']").each(function() {
                    if ($(dropdown).val() > 0)
                        $(this).hide("fast");
                    else
                        $(this).show("fast");
                });
            };
                        
            function cascadeOperation(uid, origCombos, obj, eachFunc, isInitial) {
                var DIV_SEL = "div#" + uid;
                checkErrorVisibility(obj);
                var change_handler_js = eval("dropdownChangeHandler_" + uid);
                if (change_handler_js)
                    change_handler_js(obj);
                $(DIV_SEL + " [parent_id=" + obj.id + "]").each(function(idx){
                    eachFunc(uid, origCombos, this, obj, isInitial);
                    cascadeOperation(uid, origCombos, this, eachFunc, isInitial);
                });
            };

            function filterKids(uid, origCombos, obj, parent, isInitial) {
                if ($(parent).val() > 0) {
                    if (isInitial === false)
                        $(obj).html(origCombos[obj.id].html());
                    $("#" + obj.id + " option[value != '0'][reference != '" + $(parent).val() + "']").remove();
                    if (isInitial === false)
                        $(obj).parent().slideDown('fast');
                } else {
                    $(obj).val(0);
                    $(obj).empty();
                    $(obj).parent().hide();
                };
            };
            
            function getMaxElemsWidth(jquery_elems) {
                Array.max = function(array) {
                    return Math.max.apply(Math, array);
                };
                var widths= jquery_elems.map(function() {
                    return $(this).outerWidth();
                }).get();
                return Array.max(widths);
            };
            
            function checkLinksPlacement(uid) {
                var DIV_SEL = "div#" + uid;
                
                $(DIV_SEL + " [class='span_add_link']").each(function() {
                    var tiedTo = $(this).attr("tied_to");
                    if (tiedTo)
                        if ($(this).prev().attr("id") !== tiedTo)
                            $(this).insertAfter("#" + tiedTo);
                });
            };

            function documentReadyInitialization(uid, origCombos) {
                
                $(document).ready(function(){
                    
                    var DIV_SEL = "div#" + uid;
                    
                    checkLinksPlacement(uid);
                    
                    $(DIV_SEL + " .generic-widget").each(function(idx){
                        origCombos[this.id] = $(this).clone();
                    });
                
                    $(DIV_SEL + " .generic-widget:last").each(function(idx){
                    
                        if ($(this).val() > 0) {
                            parent = $("#" + $(this).attr("parent_id"));
                            reference = $(this).find(":selected").attr("reference");
                            while (reference > 0) {
                                $(parent).val(reference);
                                reference = $(parent).find(":selected").attr("reference");
                                parent = $("#" + $(parent).attr("parent_id"));
                            };
                        };
                    });
                
                    $(DIV_SEL + " .generic-widget:first").each(function(idx){
                        cascadeOperation(uid, origCombos, this, filterKids, true);
                    });
                
                   $(DIV_SEL + " .generic-widget").change(function(){
                        cascadeOperation(uid, origCombos, this, filterKids, false);
                    });
                
                });
            };

            function showAddDialog(uid, ajax_url, opts) {
                
                var DIV_SEL = "div#" + opts.dlg_name;
                
                function isString(o) {
                    return typeof o == "string" || 
                           (typeof o == "object" && 
                            o.constructor === String);
                };
                
                function replaceTopLevel() {
                    try {
                        var sel = $(DIV_SEL + " [id='" + opts.parent + "']");
                        $(sel).parent().hide();
                        $($(sel).parent()).after("<td class='" + $(sel).parent().attr("class") + "'>" + 
                                                 "<span id='" + opts.parent + "_replacement'>" + 
                                                 $("option:selected", sel).text() + "</span></td>");
                        $(DIV_SEL + " input:visible:enabled:first").focus();
                    } catch (e) { };
                };
    
                if (!isString(opts.dlg_title))
                    opts.dlg_title = "Add record";
                    
                opts.autoOpen = false;
                opts.modal = true;
                opts.minHeight = 100;
                opts.minWidth = 300;

                if (opts.dialog_width > 0)
                    opts.width = opts.dialog_width;
                if (opts.dialog_height > 0)
                    opts.height = opts.dialog_height;
                
                $(DIV_SEL).remove();
                $("body").append('<div id="' + opts.dlg_name + '" title="' + opts.dlg_title + '"></div>');
                $(DIV_SEL).html("Loading...");
                $(DIV_SEL).dialog(opts);
                $(DIV_SEL).bind("dialogclose", function(event, ui) {
                    $(DIV_SEL).remove();
                });
                
                $(DIV_SEL).dialog("open");
                
                if (!opts.ajax_data)
                    opts.ajax_data = {};
                opts.ajax_data[uid + "_operation"] = "ajax_dialog_content";
                opts.ajax_data[uid + "_widget"] = uid;
                opts.ajax_data[uid + "_dialog"] = opts.dlg_name;
                opts.ajax_data[uid + "_target"] = opts.target;
                opts.ajax_data[uid + "_parent_value"] = $("#" + opts.parent).val();
                
                function form_submit() {
                    if ($(this).data("isSubmitted"))
                        return false;
                    $(this).data("isSubmitted", true);
                    
                    var req_data = uid + "_widget=" + uid + "&" + uid + "_operation=ajax_dialog_submit&" + 
                        uid + "_target=" + opts.target + "&" + $(this).serialize();
                    $(DIV_SEL).html("Please wait...");
                    
                    $.post(ajax_url, req_data, function (data) {
                        
                        if (data.substring(0,14) !== "<!-- items -->") {
                            $(DIV_SEL).html(data);
                            $(DIV_SEL + " form:first").data("isSubmitted", false);
                            if ($(DIV_SEL + " form:first").length > 0) {
                                $(DIV_SEL + " form:first").submit(form_submit);
                                replaceTopLevel();
                            };
                        } else {
                            combo = opts.target.replace(".", "_");
                            var origCombos = eval("origCombos_" + uid);
                            origCombos[combo].html(data);
                            $("#" + combo).html(data);
                            parent = $("#" + $("#" + combo).attr("parent_id"));
                            $(parent).each(function(idx){
                                cascadeOperation(uid, origCombos, this, filterKids, false);
                            });
                            $("#" + combo).trigger("change");
                            $(DIV_SEL).dialog("close");
                        };
                    });
                    
                    return false;
                };
                
                $(DIV_SEL).load(ajax_url, opts.ajax_data,
                                     function (response, status, xhr) {
                                         if (status == "error") {
                                             var msg = "Loading error: ";
                                             $(DIV_SEL).html(msg + xhr.status + " " + xhr.statusText);
                                         } else {
                                             $(DIV_SEL + " form:first").submit(form_submit);
                                             replaceTopLevel();
                                             if (!opts.width)
                                                 $(DIV_SEL).dialog("option", "width", getMaxElemsWidth($(DIV_SEL + " table")) + 30);
                                             if (!opts.height)
                                                 $(DIV_SEL).dialog("option", "height", $(DIV_SEL + " form").outerHeight(true) + 60);
                                             $(DIV_SEL).dialog("option", "position", "center");
                                         };
                                     });
                                     
            };
            
        ''' % args

    def get_widget_js(self, **args):
        return SCRIPT('''
            %(shared_code)s
            
            var origCombos_%(uid)s = {};
            
            var dropdownChangeHandler_%(uid)s = %(change_handler_js)s;
            
            documentReadyInitialization("%(uid)s", origCombos_%(uid)s);
        ''' % args, _type="text/javascript")
