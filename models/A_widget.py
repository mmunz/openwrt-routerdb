# coding: utf8
from gluon.sqlhtml import *

class SELECT_OR_ADD_OPTION(object):  #and even EDIT

    def __init__(self, referenced_table, controller="default", function="referenced_data", dialog_width=450):
        self.referenced_table = referenced_table
        self.controller = controller
        self.function = function
        self.dialog_width = dialog_width

    def widget(self, field, value):
        #generate the standard widget for this field
        select_widget = OptionsWidget.widget(field, value)

        #get the widget's id (need to know later on so can tell receiving controller what to update)
        my_select_id = select_widget.attributes.get('_id', None) 
        wrapper = DIV(_id=my_select_id+"__reference-actions__wrapper") 
        wrapper.components.extend([select_widget, ])
        style_icons = {'new':"icon plus icon-plus", 'edit': "icon pen icon-pencil" }
        actions = ['new']
        if value: actions.append('edit')  # if we already have selected value
        for action in actions:

            extra_args = [my_select_id, action, self.referenced_table]

            if action == 'edit':
                extra_args.append(value)

            #create a div that will load the specified controller via ajax
            form_loader_div = DIV(LOAD(c=self.controller, f=self.function, args=extra_args, ajax=True), _id=my_select_id+"_"+action+"_dialog-form", _title=action+": "+self.referenced_table)
            #generate the "add/edit" button that will appear next the options widget and open our dialog
            action_button = A([SPAN(_class=style_icons[action]), SPAN( _class="buttontext button") ], 
                              _title=T(action), _id=my_select_id+"_option_%s_trigger"%action, _class="button btn", _style="vertical-align:top" )
    
            #create javascript for creating and opening the dialog
            js = '$( "#%s_%s_dialog-form" ).dialog({autoOpen: false, not__modal:true, show: "blind", hide: "explode", width: %s});' % (my_select_id, action,  self.dialog_width)
            # soma: component handler added so recursive works
            js += '$( "#%s_option_%s_trigger" ).click(function() { $( "#%s_%s_dialog-form" ).dialog( "open" );jQuery.web2py.component_handler("#%s_%s_dialog-form");return false;}); ' % (my_select_id, action, my_select_id, action, my_select_id, action, )
            js += '$(function() { $( "#%s_option_%s_trigger" ).button({text: true, icons: { primary: "ui-icon-circle-plus"} }); });' % (my_select_id, action, )

            if action=='edit':
                # hide if reference changed - as load is constructed for initial value only (or would need some lazy loading mechanizm)
                js += '$(function() {$("#%s").change(function() {    $( "#%s_option_%s_trigger" ).hide(); } ) });' % (my_select_id,  my_select_id, 'edit', )
            #if action == 'new':
            #    js += '$(function() { jQuery.web2py.component_handler("#%s_%s_dialog-form") });' % (my_select_id, action)


            jq_script=SCRIPT(js, _type="text/javascript")
    
            wrapper.components.extend([form_loader_div, action_button, jq_script])
        return wrapper

class SELECT_OR_ADD_OPTION_MULTIPLE(object):  #and even EDIT

    def __init__(self, referenced_table, controller="default", function="referenced_data", dialog_width=480):
        self.referenced_table = referenced_table
        self.controller = controller
        self.function = function
        self.dialog_width = dialog_width

    def widget(self, field, value):

        from plugin_multiselect_widget import (
            hmultiselect_widget, vmultiselect_widget,
            rhmultiselect_widget, rvmultiselect_widget,
        )
        #generate the standard widget for this field
        #select_widget = OptionsWidget.widget(field, value)

        select_widget = hmultiselect_widget(field, value)

        #get the widget's id (need to know later on so can tell receiving controller what to update)
        my_select_id = select_widget.attributes.get('_id', None)
        wrapper = DIV(_id=my_select_id+"__reference-actions__wrapper") 
        wrapper.components.extend([select_widget, ])
        style_icons = {'new':"icon plus icon-plus", 'edit': "icon pen icon-pencil" }
        actions = ['new']
        js = ''


        if value:
            actions.append('edit')  # if we already have selected value

        for action in actions:
            extra_args = [my_select_id, action, self.referenced_table]
            extra_vars = dict()
            #if self.referenced_table == "firmware":
            #    extra_vars=dict(id_parent=request.args[-1])
            form_loader_div = []
            action_buttons = []

            if action == 'new':
                action_buttons.append(A([SPAN(_class=style_icons[action]), SPAN( _class="buttontext button") ],
                     _title=T(action), _id=my_select_id+"_option_%s_trigger"%action, _class="button btn", _style="vertical-align:top" ))

                form_loader_div.append(DIV(LOAD(c=self.controller, f=self.function, args=extra_args, vars=extra_vars, ajax=True), _id=my_select_id+"_"+action+"_dialog-form", _title=action+": "+self.referenced_table))
                #create javascript for creating and opening the dialog
                js += '$( "#%s_%s_dialog-form" ).dialog({autoOpen: false, not__modal:true, show: "blind", hide: "explode", width: %s});' % (my_select_id, action,  self.dialog_width)
                # soma: component handler added so recursive works
                # js += '$( "#%s_option_%s_trigger" ).click(function() { $( "#%s_%s_dialog-form" ).dialog( "open" );jQuery.web2py.component_handler("#%s_%s_dialog-form");return false;}); ' % (my_select_id, action, my_select_id, action, my_select_id, action, )
                js += '$( "#%s_option_%s_trigger" ).click(function() { $( "#%s_%s_dialog-form" ).dialog( "open" );jQuery.web2py.component_handler("#%s_%s_dialog-form");return false;}); ' % (my_select_id, action, my_select_id, action, my_select_id, action, )
                js += '$(function() { $( "#%s_option_%s_trigger" ).button({text: true, icons: { primary: "ui-icon-circle-plus"} }); });' % (my_select_id, action, )


            if action == 'edit':

                for v in value:
                    this_select_id = my_select_id + "-" + str(v)
                    extra = []
                    for d in extra_args:
                        extra.append(d)
                    extra.append(v)

                    action_buttons.append(A([SPAN(_class=style_icons[action]), SPAN( _class="buttontext button") ],
                         _title=T(action), _id=this_select_id+"_option_edit_trigger", _class="button btn", _style="vertical-align:top" ))


                    #create javascript for creating and opening the dialog
                    #js += 'alert("create ' + this_select_id + '");'
                    js += '$("#%s_edit_dialog-form" ).dialog({autoOpen: false, not__modal:true, show: "blind", hide: "explode", width: %s});' % (this_select_id, self.dialog_width)
                    # soma: component handler added so recursive works
                    # js += '$( "#%s_option_%s_trigger" ).click(function() { $( "#%s_%s_dialog-form" ).dialog( "open" );jQuery.web2py.component_handler("#%s_%s_dialog-form");return false;}); ' % (this_select_id, action, this_select_id, action, this_select_id, action, )
                    js += '$( "#%s_option_edit_trigger" ).click(function() { $( "#%s_edit_dialog-form" ).dialog( "open" );jQuery.web2py.component_handler("#%s_edit_dialog-form");return false;}); ' % (this_select_id, this_select_id, this_select_id )
                    js += '$(function() { $( "#%s_option_edit_trigger" ).button({text: true, icons: { primary: "ui-icon-circle-plus"} }); });' % (this_select_id )

                    js += '$( "#%s_option_edit_trigger").hide();' % (this_select_id )
                    js += """$(function() {
                               $("#%s").change(function() {
                                   // show edit button only for the selected value
                                   var selected = $('#%s :selected').val();
                                   // add missing buttons
                                   // <div id="router_id_flash__reference-actions__wrapper" - da muss der button rein
                                   //var newlink = '<a class="button btn" data-w2p_disable_with="default" id="router_id_flash-' + selected + '_option_edit_trigger" style="vertical-align:top" title="edit"><span class="icon pen icon-pencil"></span><span class="buttontext button"></span></a>';
                                   //$("#router_id_flash__reference-actions__wrapper").append(newlink);
                                   //var dialog='<div id="router_id_flash-3_edit_dialog-form" title="edit: flash"><div data-w2p_remote="/routerdb/referenced_data/router_id_flash/edit/flash/"' + selected + ' id="c0289544368488">loading...</div></div>';
                                   //$("body").append(dialog);
                                   //alert("selected " + selected);
                                   $( "#%s-" + selected + "_option_edit_trigger" ).show();
                               } )
                            });""" % (my_select_id, my_select_id, my_select_id)

                    form_loader_div.append(DIV(LOAD(c=self.controller, f=self.function, args=extra, ajax=True), _id=this_select_id+"_"+action+"_dialog-form", _title=action+": "+self.referenced_table))
    
            #if action=='edit':
                # hide per default, show when one option is selected
            #if action == 'new':
            #    js += '$(function() { jQuery.web2py.component_handler("#%s_%s_dialog-form") });' % (my_select_id, action)


            jq_script=SCRIPT(js, _type="text/javascript")

            content = []
            for div in form_loader_div:
                content.append(div)
    
            for a in action_buttons:
                content.append(a)

            content.append(jq_script)
                
            #wrapper.components.extend([form_loader_div, action_button, jq_script])
            wrapper.components.extend(content)
        return wrapper
