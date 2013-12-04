# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #return dict(message=T('Hello World'), content="foo")
    return auth.wiki()

def router():
    items = db(db.router)
    response.files.append(URL('static','js/jquery.dataTables.min.js'))
    response.files.append(URL('static','js/jquery.dataTables.custom.js'))
    response.files.append(URL('static','css/jquery.dataTables175.css'))
    response.files.append(URL('static','css/jquery.dataTables.css'))
    return dict(items=items)

def routerdetail():
    item_slug = request.args(0)
    query = (db.router.slug == item_slug)
    item = db(query).select().first()
    if not item:
        redirect(URL(request.application, request.controller,'router')) 
    response.title = '%s %s' % (item.id_manufacturer.name, item.model)

    # Format links
    baseurl_toh = "http://wiki.openwrt.org/toh/"
    baseurl_wikidevi = "http://wikidevi.com/wiki/"
    links = []
    if item.toh:
        links.append(A('%s - %s' % (item.model, T('OpenWrt Table of Hardware')), _href=baseurl_toh + item.toh,
                     _title=item.toh + ' - Table of Hardware'))
    if item.wikidevi:
        links.append(A('%s - %s' % (item.model, T('Wikidevi')), _href=baseurl_wikidevi + item.wikidevi,
                     _title=item.wikidevi + ' - Wikidevi'))

    # format antennas
    antennas = []
    if item.id_antenna:
        for a in item.id_antenna:
            query = (db.antenna.id == a)
            ant = db(query).select().first()

            if ant:
                gain = ant.gain
                connector = ant.id_connector.connector

                ant_formatted = None
                if gain and connector:
                    ant_formatted = '%s db (%s)' % (gain, connector)
                elif gain:
                    ant_formatted = '%s db' % (gain)
                elif connector:
                    ant_formatted = '%s' % (connector)

                if ant_formatted:
                    antennas.append(ant_formatted)

    # format usb
    usbports = []
    if item.id_usb:
        for u in item.id_usb:
            query = (db.usb.id == u)
            usb = db(query).select().first()

            if usb:
                ports = usb.ports
                modus = None
                if usb.id_modus:
                    modus = usb.id_modus.modus

                usb_formatted = '-'
                if ports and modus:
                    usb_formatted = '%s x USB %s' % (ports, modus)
                elif ports:
                    usb_formatted = ports
                elif modus:
                    usb_formatted = modus

                usbports.append(usb_formatted)

    # format serial
    serial = []
    if item.id_serial:
        for s in item.id_serial:
            if s:
                baud = None
                insert = True

                if s.id_baud:
                    baud = s.id_baud.baud
                solder = s.solder

                serial_formatted = '-'
                if solder and baud:
                    serial_formatted = '%s (%s)' % (baud, T('requires soldering'))
                else:
                    serial_formatted = baud

                for k in serial:
                    if k['formatted'] == serial_formatted:
                        k['count'] = k['count'] + 1
                        insert = False
                if insert:
                    serial.append({'count': 1, 'formatted':serial_formatted})

    # format ram
    ram = []
    for r in item.id_ram:
        insert = True
        ram_formatted = '%s %s' % (r.id_manufacturer.name, r.model)

        print r.slug
        for k in ram:
            print k['formatted']
            print  ram_formatted
            if k['formatted'] == ram_formatted:
                k['count'] = k['count'] + 1
                insert = False
        if insert:
            ram.append({'count': 1, 'formatted': ram_formatted, 'slug': r.slug})


    # format wifi
    wifihw = []
    if item.id_wifi:
        for w in item.id_wifi:
            chipset = ''
            rev = ''
            modes = ''
            vap = ''
            query = (db.wifi.id == w)
            wifi = db(query).select().first()

            m = wifi.id_manufacturer
            manufacturer = A(m.name,
                              _href=URL(
                                'manufacturer', item.id_manufacturer.slug
                              ),
                              _title=m.namefull or m.name
                            )

            chipset = wifi.id_chipset.chipset
            if wifi.id_chipset.rev:
                chipset = chipset + '-rev' + wifi.id_chipset.rev
            vap = T('No')
            if wifi.id_chipset.vap:
                vap = T('Yes')

            wifihw.append({
                'manufacturer': manufacturer,
                'chipset': chipset,
                'modes': wifi.id_modes.modes,
                'vap': vap
            })

    # format network
    network = []
    if item.id_network:
        for n in item.id_network:
            chipset = ''
            rev = ''
            speed = ''
            vlan = ''
            query = (db.network.id == n)
            net = db(query).select().first()

            m = net.id_manufacturer
            manufacturer = A(m.name,
                              _href=URL(
                                'manufacturer', item.id_manufacturer.slug
                              ),
                              _title=m.namefull or m.name
                            )

            chipset = net.id_chipset.chipset
            if net.id_chipset.rev:
                chipset = chipset + '-rev' + net.id_chipset.rev
            vlan = T('No')
            if net.id_chipset.vlan:
                vlan = T('Yes')

            network.append({
                'manufacturer': manufacturer,
                'chipset': chipset,
                'speed': net.id_speed.speed,
                'ports': net.ports,
                'vlan': vlan
            })

    # format firmware
    firmware = []
    for f in item.id_firmware:
        query = (db.firmware.id == f)
        fw = db(query).select().first()
        release = fw.id_openwrt_versions.name
        downloadurl = fw.id_openwrt_versions.downloadurl
        target = fw.target
        subtarget = fw.subtarget
        profile = fw.profile or '-'
        sysupgrade = fw.sysupgrade
        factory = fw.factory
        release_slug = fw.id_openwrt_versions.slug

        firmware.append({
            'release': release,
            'target': target,
            'subtarget': subtarget,
            'downloadurl': downloadurl,
            'profile': profile,
            'factory': factory,
            'sysupgrade': sysupgrade,
            'release_slug': release_slug,
        })

    return dict(item=item, ram=ram, links=links, antennas=antennas, usbports=usbports, serial=serial,
                wifi=wifihw, network=network, firmware=firmware)

def edit():
    from plugin_multiselect_widget import (
        hmultiselect_widget, vmultiselect_widget,
        rhmultiselect_widget, rvmultiselect_widget,
    )

    if request.args(-1):
        item_slug = request.args(-1)
        query = (db.router.slug == item_slug)
        item = db(query).select().first()
        if item:
            request.args[-1] = item.id

    db.router.id.readable = False
    db.router.id_ram.readable = False
    db.router.id_flash.readable = False
    db.router.note.readable = False
    db.router.id_manufacturer.readable = False
    #db.router.model.readable = False

    # limit available options shown for firmware
    # this is a ugly workaround:
    # if form is just displayed limit to firmwares which the router.db.id_firmware references
    # if the form is updated relax this restriction, so new records can be inserted
    if len(request.args) > 1 and request.args[1] == 'edit':
        if not request.vars.id_firmware:
            firmware = db.router[request.args[-1]].id_firmware
            query = db.firmware.id.belongs(firmware)
            db.router.id_firmware.requires = IS_IN_DB(db(query), db.firmware.id, lambda row: db.openwrt_versions[row.id_openwrt_versions].name, multiple=True)


    links = [
    #dict(
    #    header='Model',
    #    body = lambda row: A(row.model,_href=URL('edit', args=['router', 'view', 'router', row.slug]))
    #    ),
    #dict(
    #    header='Manufacturer',
    #    body = lambda row: A(row.id_manufacturer.name,_href=URL('manufacturer', args=[row.id_manufacturer.slug]))
    #    ),
    ]


    form = SQLFORM.smartgrid(
        db.router,
        orderby = dict(
                     manufacturer=[db.manufacturer.name.lower()],
                     ram=[db.ram.model.lower()],
                  ),
        linked_tables=['ram', 'manufacturer', 'flash', 'board', 'uploads'],
        showbuttontext=False,
        csv=False,
        links=links,
        user_signature=True,
        create=True, deletable=False, editable=True, details=True,
        searchable=True,
        ui='jquery-ui',
    )
    db.router.id_flash.widget = hmultiselect_widget


    return dict(form=form)

def ram():
    item_slug = request.args(0)
    query = (db.ram.slug == item_slug)
    item = db(query).select().first()
    response.title = '%s - %s' % (item.id_manufacturer.name, item.model)
    return dict(item=item)

def flash():
    item_slug = request.args(0)
    query = (db.flash.slug == item_slug)
    item = db(query).select().first()
    response.title = '%s - %s' % (item.id_manufacturer.name, item.model)
    return dict(item=item)

def cpu():
    item_slug = request.args(0)
    query = (db.cpu.slug == item_slug)
    item = db(query).select().first()
    response.title = '%s - %s' % (item.id_manufacturer.name, item.model)
    return dict(item=item)

def architecture():
    item_slug = request.args(0)
    query = (db.architecture.slug == item_slug)
    item = db(query).select().first()
    if item.rev:
        response.title = '%s - %s' % (item.arch, item.rev)
    else:
        response.title = item.arch

    return dict(item=item)

def platform():
    item_slug = request.args(0)
    query = (db.platform.slug == item_slug)
    item = db(query).select().first()
    response.title = '%s %s' % (item.id_manufacturer.name, item.model)
    return dict(item=item)

def manufacturer():
    item_slug = request.args(0)
    query = (db.manufacturer.slug == item_slug)
    item = db(query).select().first()
    print(item)
    response.title = item.name
    return dict(item=item)

def firmware():
    item_slug = request.args(0)
    query = (db.openwrt_versions.slug == item_slug)
    item = db(query).select().first()
    response.title = '%s' % item.name
    return dict(item=item)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def download():
    return response.download(request, db)

@cache.action()
#def api():
#    session.forget()
#    return service()

@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def referenced_data(): 
    """ shows dialog with reference add/edit form
    the idea is taken from "data" function, just first argument is the id of calling select box 
    """

    try:    references_options_list_id = request.args[0]
    except: return T("ERR: references_options_list_id lacking")
    
    try:    action = request.args[1]
    except: return  T("ERR: action lacking")
    
    try:    referenced_table= request.args[2]
    except: return T("ERR: referenced_table lacking")

    if action=="edit":
        try: referenced_record_id = int( request.args[3] )
        except: response.flash = T("ERR: referenced_record_id lacking"); return (response.flash)
        form = SQLFORM(db[referenced_table], referenced_record_id) # edit/update/change
    else:
        form = SQLFORM(db[referenced_table]) # new/create/add

    if form.accepts(request.vars):
        #Then let the user know adding via our widget worked
        response.flash = "done: %s %s" %( T(action),  referenced_table) # added / edited
        #close the widget's dialog box
        response.js = '$( "#%s_%s_dialog-form" ).dialog( "close" ); ' %(references_options_list_id, action)

        # if using ADD_OR_SELECT_OPTION_MULTIPLE the references_options_list_id
        # is a div and the new option must be inserted there. If using the normal
        # widget it is a select.

        references_options_list_selected_id = references_options_list_id.split('_')[1] + "_" + references_options_list_id.split('_')[2]

        response.js += """htmltag=$("#%s").prop("tagName");""" % references_options_list_id
        response.js += """if (htmltag == "DIV") { targetdiv = "#%s" } else { targetdiv = "#%s" };""" % (references_options_list_selected_id, references_options_list_id)


        def format_referenced(id): 
            #return format(db[referenced_table], id)  #should get from table
            table = db[referenced_table]
            if isinstance(table._format, str):     return table._format % table[id]
            elif callable(table._format):          return table._format(table[id])        
            else: return "???"
            
        if action=='new':
            #update the options they can select their new category in the main form
            response.js += """$(targetdiv).append("<option value='%s'>%s</option>");""" % (form.vars.id, format_referenced(form.vars.id))
            #and select the one they just added
            response.js += """$(targetdiv).val("%s");""" % (form.vars.id)
        if action=='edit':
            #response.js += """alert( $('#%s option[value="%s"]').html());""" % (references_options_list_id, form.vars.id) # format_referenced(form.vars.id) )
            response.js += """$('#%s option[value="%s"]').html('%s')""" % (references_options_list_id, form.vars.id, format_referenced(form.vars.id) )
        
    return BEAUTIFY(form)


#@service.json
#def status():
#    response.view = 'generic.json'
#    import json
#    query = (db.router.id > 0)
#    routers = db(query).select()
#    ret = json.loads(routers)
#    return dict(ret=ret)


@request.restful()
def api_datatables():
    response.view = 'generic.'+request.extension

    def GET(search, **vars):
        try:
            rows = db.smart_query([db.router,db.ram, db.manufacturer, db.flash, db.cpu],search).select()

            aaData = []
            for row in rows:

                # resolve list parameters
                cpumodels = []
                cpuspeeds = []
                for c in row.id_cpu:
                    cpumodels.append(c.model)
                    cpuspeeds.append(c.speed)
                

                # datatables json requires aaData to be specificly formatted
                atxt = {}
                atxt['0'] = row.id_manufacturer and row.id_manufacturer.name
                atxt['1'] = row.model
                atxt['2'] = row.rev
                atxt['3'] = row.id_platform and row.id_platform.model or '-'
                atxt['4'] = cpumodels,
                atxt['5'] = cpuspeeds,
                atxt['6'] = row.ramsize
                atxt['7'] = row.flashsize
                aaData.append(atxt)

            result = {
                'aaData': aaData,
                'sEcho': request.vars.sEcho,
                'iTotalRecords': len(rows),
            }

            return dict(result)
        except RuntimeError:
            raise HTTP(400,"Invalid search string")
    return locals()

@request.restful()
def api():
    response.view = 'generic.'+request.extension
    def GET(**vars):
        if request.vars['search']:
            search = request.vars['search']
        else:
            search = False

        if request.vars['get'] == 'manufacturer':
            # output all router manufacturers
            # query = (db.router.id_manufacturer >= 0)
            # rows = db(query).select()
            if not search:
                search = 'router.id_manufacturer greater than 0'
            else:
                search = 'router.id_manufacturer greater than 0 and ' + search

            rows = db.smart_query([db.router, db.manufacturer],search).select()

            out = []
            for r in rows:
                row = {
                    'id': r.id_manufacturer.id,
                    'manufacturer': r.id_manufacturer.name,
                    'slug': r.id_manufacturer.slug,
                }
                if not row in out:
                    out.append(row)

            #rows = [ 1,2]
            return dict(result=out)

        if request.vars['get'] == 'router':
            # output all router manufacturers
            # query = (db.router.id_manufacturer >= 0)
            # rows = db(query).select()
            if not search:
                search = 'router.id greater than 0'
            else:
                search = 'router.id greater than 0 and ' + search

            rows = db.smart_query([db.router],search).select()
            print rows

            out = []
            for r in rows:
                firmware = []
                for f in r.id_firmware:
                    resolved = {
                        'release': f.id_openwrt_versions.name,
                        'target': f.target,
                        'subtarget': f.subtarget,
                        'profile': f.profile,
                        'factory': f.factory,
                        'sysupgrade': f.sysupgrade
                    }
                    firmware.append(resolved)

                row = {
                    'id': r.id,
                    'model': r.model,
                    'rev': r.rev,
                    'manufacturer': r.id_manufacturer.name,
                    'slug': r.slug,
                    #'id_ram': r.id_ram,
                    'ramsize': r.ramsize,
                    'flashsize': r.flashsize,
                    'thumbnail': r.thumbnail,
                    'firmware': firmware,
                }
                if not row in out:
                    out.append(row)

            #rows = [ 1,2]
            return dict(result=out)


        else:
            try:
                rows = db.smart_query([db.router, db.ram, db.manufacturer, db.flash, db.cpu],search).select()
                # seems there is no simple way to filter the smartquery, so do it the dumb way:
                out = []
                for r in rows:
                    if r.is_active:
                        del r["is_active"]
                        del r["created_on"]
                        del r["created_by"]
                        del r["modified_on"]
                        del r["modified_by"]
                        out.append(r)

                rows = out


                """ this will do recursion for 1 level
                for r in rows:
                    for k in r.keys():
                        if k.startswith('id_'):
                            if type(r[k]).__name__ == 'Reference':
                                table = k.replace('id_', '')
                                query = (db[table].id == r[k])
                                item = db(query).select()
                                if item:
                                    r[k] = item[0]

                            print(type(r[k]).__name__)
                            if type(r[k]).__name__ == 'list':
                                table = k.replace('id_', '')
                                references = []
                                for ref in r[k]:
                                    query = (db[table].id == ref)
                                    refitem = db(query).select()
                                    if refitem:
                                        references.append(refitem[0])
                                if len(references) > 0:
                                        r[k] = references
                """
                        
                return dict(result=rows)
            except RuntimeError:
                raise HTTP(400,"Invalid search string")
    #def POST(table_name,**vars):
    #    return db[table_name].validate_and_insert(**vars)
    return locals()
