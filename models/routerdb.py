from applications.routerdb.modules.countries import *
from gluon import current
from smartthumb import SMARTHUMB
from datetime import datetime
settings = Storage()

def get_aggregate(fields, table, field):
    """aggregates all values for ids which are referenced in
       list:reference fields.

        Args:
          fields(list): The list containing all referenced ids
          table: The table to work with
          field(str): whic field to get for each id of the referenced table

        Returns:
          Aggregated value for all referenced fields 
    """

    value = 0
    for f in fields:
        flash = table[int(f)]
        try:
            value = value + flash[field]
        except:
            pass         

    return value

def format_slug(primary, sec):
    if sec:
        return IS_SLUG()(primary + ' ' + sec)[0]
    else:
        return IS_SLUG()(primary)[0]

def format_connector(connector, gain):
    if gain:
        return '%s %sdb' % (connector, gain)
    else:
        return connector

def format_usb(ports, type):
    if type:
        return '%s x USB %s' % (ports, type)
    else:
        return ports

def format_serial(baud, solder):
    if solder:
        return '%s (soldering required)' % (baud)
    else:
        return baud

def format_wifi(chipset, rev):
    if rev:
        return '%s-rev%s' % (chipset, rev)
    else:
        return chipset

def format_network(chipset, rev, speed, ports):
    if rev:
        return '%s-rev%s-%sMbps-%s Ports' % (chipset, rev, speed, ports)
    else:
        return '%s-%sMbps-%s Ports' % (chipset, speed, ports)

def format_wifimode(b, g, a, n, ac):
    modes = []
    if b:
        modes.append('b')
    if g:
        modes.append('g')
    if a:
        modes.append('a')
    if n:
        modes.append('n')
    if ac:
        modes.append('ac')

    return ', '.join(modes)

uploadfolder = os.path.join(request.folder,('uploads/'))

#db.define_table('uploads',
#    Field('name','string'),
#    Field('mainfile','upload', uploadfolder=uploadfolder),
#    Field('thumb','upload',writable=False,readable=False),
#    format = '%(mainfile)s'
#)

db.define_table("manufacturer",
    Field("name", "string", unique=True),
    Field("country", requires=IS_IN_SET(COUNTRIES)),
    Field("url",
        requires=IS_EMPTY_OR(IS_URL(error_message=T('%(name)s is invalid') % dict(name=T('URL'))))
    ),
    Field("slug", "string", compute=lambda row: IS_SLUG()(row.name)[0]),
    Field("namefull", "string"),
    auth.signature,
    format = '%(name)s',
)

db.define_table("ram",
    Field("id_manufacturer", db.manufacturer, widget=SELECT_OR_ADD_OPTION("manufacturer").widget, label="Manufacturer"),
    Field("model", "string", unique=True),
    Field("slug", "string", compute=lambda row: IS_SLUG()(row.model)[0]),
    Field("mb", "integer"),
    #Field("date_inserted", "datetime", default = datetime.today(), writable=False),
    #Field("date_modified", "datetime", compute=lambda row: datetime.today()),
    auth.signature,
    format = '%(model)s',
)

db.define_table("platform",
    Field("id_manufacturer", db.manufacturer, widget=SELECT_OR_ADD_OPTION("manufacturer").widget, label="Manufacturer"),
    Field("model", "string", unique=True),
    Field("rev", "string"),
    Field("slug", "string", compute=lambda row: IS_SLUG()(row.model)[0]),
    auth.signature,
    format = '%(model)s %(rev)s',
)

db.define_table("architecture",
    Field("arch", "string"),
    Field("rev", "string"),
    Field("slug", "string", compute=lambda row: format_slug(row.arch, row.rev)),
    auth.signature,
    format = '%(arch)s %(rev)s',
)

db.define_table("cpu",
    Field("id_manufacturer", db.manufacturer, widget=SELECT_OR_ADD_OPTION("manufacturer").widget, label="Manufacturer"),
    Field("model", "string"),
    Field("rev", "string"),
    Field("id_architecture", db.architecture, widget=SELECT_OR_ADD_OPTION("architecture").widget, label="Architecture"),
    Field("slug", "string", compute=lambda row: format_slug(row.model, row.rev)),
    Field("speed", "integer"),
    auth.signature,
    format = '%(model)s',
)


db.define_table("flash",
    Field("id_manufacturer", db.manufacturer, widget=SELECT_OR_ADD_OPTION("manufacturer").widget, label="Manufacturer"),
    Field("model", "string", unique=True),
    Field("slug", "string", compute=lambda row: IS_SLUG()(row.model)[0]),
    Field("mb", "integer"),
    auth.signature,
    format = '%(model)s',
)


db.define_table("usb_modes",
    Field("modus", "string", unique=True),
    auth.signature,
    format = '%(modus)s',
)

db.define_table("usb",
    Field("id_modus", db.usb_modes, widget=SELECT_OR_ADD_OPTION("usb_modes").widget, label=T('Type')),
    Field("ports", "integer"),
    auth.signature,
    format = lambda row: format_usb(row.ports, db.usb_modes[row.id_modus].modus)
)

db.define_table("baudrates",
    Field("baud", "string", unique=True),
    auth.signature,
    format = '%(baud)s',
)

db.define_table("serial",
    Field("id_baud", db.baudrates, required=True, widget=SELECT_OR_ADD_OPTION("baudrates").widget, label=T('Baudrate')),
    Field("solder", "boolean", label=T('Requires soldering')),
    auth.signature,
    format = lambda row: format_serial(db.baudrates[row.id_baud].baud, row.solder)
)

db.define_table("connectors",
    Field("connector", "string", label=T('Connector')),
    Field("slug", "string", compute=lambda row: IS_SLUG()(row.connector)[0]),
    auth.signature,
    format = '%(connector)s',
)

db.define_table("antenna",
    Field("gain", "integer", label=T('Gain (db)')),
    Field("id_connector", db.connectors, widget=SELECT_OR_ADD_OPTION("connectors").widget, label=T('Connector')),
    Field("slug", "string", compute=lambda row: format_slug(row.connector.connector, row.gain)),
    auth.signature,
    format = lambda row: format_connector(db.connectors[row.id_connector].connector, row.gain)
)

db.define_table("wifi_chipsets",
    Field("chipset", "string", label=T('Chipset')),
    Field("rev", "string", label=T('Revision')),
    Field("vap", "boolean", label=T('Supports VAP')),
    Field("slug", "string", compute=lambda row: format_slug(row.chipset, row.rev)),
    auth.signature,
    format = lambda row: format_wifi(row.chipset, row.rev),
)

db.define_table("wifimodes",
    Field("x11b", "boolean", label=T('802.11b')),
    Field("x11g", "boolean", label=T('802.11g')),
    Field("x11a", "boolean", label=T('802.11a')),
    Field("x11n", "boolean", label=T('802.11n')),
    Field("x11ac", "boolean", label=T('802.11ac')),
    Field("modes", compute=lambda row: format_wifimode(row.x11b, row.x11g, row.x11a, row.x11n, row.x11ac), label="RAM"),
    auth.signature,
    format = lambda row: format_wifimode(row.x11b, row.x11g, row.x11a, row.x11n, row.x11ac),
)


db.define_table("wifi",
    Field("id_manufacturer", db.manufacturer, widget=SELECT_OR_ADD_OPTION("manufacturer").widget, label="Manufacturer"),
    Field("id_chipset", db.wifi_chipsets, widget=SELECT_OR_ADD_OPTION("wifi_chipsets").widget, label=T('Chipset')),
    Field("id_modes", db.wifimodes, widget=SELECT_OR_ADD_OPTION("wifimodes").widget, label=T('Modes')),
    auth.signature,
    format = lambda row: format_wifi(db.wifi_chipsets[row.id_chipset].chipset, db.wifi_chipsets[row.id_chipset].rev)
)


db.define_table("network_chipsets",
    Field("chipset", "string", unique=True, required=True, label=T('Chipset')),
    Field("rev", "string", label=T('Revision')),
    Field("vlan", "boolean", label=T('Supports VLAN')),
    Field("slug", "string", compute=lambda row: format_slug(row.chipset, row.rev)),
    auth.signature,
    format = lambda row: format_wifi(row.chipset, row.rev),
)

db.define_table("network_speeds",
    Field("speed", "integer", required=True, label=T('Speed (Mbps)')),
    auth.signature,
    format = '%(speed)s'
)

db.define_table("network_types",
    Field("nettype", "string", unique=True, label=T('Type')),
    auth.signature,
    format = '%(nettype)s'
)


db.define_table("network",
    Field("id_manufacturer", db.manufacturer, widget=SELECT_OR_ADD_OPTION("manufacturer").widget, required=True, label="Manufacturer"),
    Field("id_chipset", db.network_chipsets, widget=SELECT_OR_ADD_OPTION("network_chipsets").widget, required=True, label=T('Chipset')),
    Field("id_type", db.network_types, widget=SELECT_OR_ADD_OPTION("network_types").widget, required=True, label=T('Type')),
    Field("id_speed", db.network_speeds, widget=SELECT_OR_ADD_OPTION("network_speeds").widget, required=True, label=T('Speed')),
    Field("ports", "integer", required=True, label=T('Ports')),
    auth.signature,
    format = lambda row: format_network(db.network_chipsets[row.id_chipset].chipset,
                                        db.network_chipsets[row.id_chipset].rev,
                                        db.network_speeds[row.id_speed].speed,
                                        row.ports)
)

db.define_table("openwrt_versions",
    Field("name", "string", unique=True, label=T('Name')),
    Field("downloadurl", requires=IS_URL(error_message=T('%(name)s is invalid') % dict(name=T('URL'))), label=T('Download URL Path')),
    Field("releasenotes", requires=IS_EMPTY_OR(IS_URL(error_message=T('%(name)s is invalid') % dict(name=T('URL')))), label=T('Release notes')),
    Field("released", "datetime", label=T('Release Date')),
    Field("rev", "string", label=T('Revision')),
    Field("slug", "string", compute=lambda row: IS_SLUG()(row.name)[0]),
    auth.signature,
    format = '%(name)s'
)

db.define_table("firmware",
    Field("id_openwrt_versions", db.openwrt_versions, widget=SELECT_OR_ADD_OPTION("openwrt_versions").widget, required=True, label="OpenWrt Release"),
    Field("target", "string", required=True, label=T('Target')),
    Field("subtarget", "string", label=T('Subtarget')),
    Field("profile", "string", label=T('Profile')),
    Field("factory", "string", label=T('Factory image')),
    Field("sysupgrade", "string", label=T('Sysupgrade image')),
    auth.signature,
    format = lambda row: db.openwrt_versions[row.id_openwrt_versions].name,
)

db.define_table("router",
    Field("id_manufacturer", db.manufacturer, widget=SELECT_OR_ADD_OPTION("manufacturer").widget, label="Manufacturer"),
    Field("manufacturer", compute=lambda row: db.manufacturer[row.id_manufacturer].name),
    Field("model", "string", unique=True),
    Field("id_platform", db.platform, widget=SELECT_OR_ADD_OPTION("platform").widget, label=T('Platform')),
    Field("rev", "string", label="Version"),
    Field("id_cpu", 'list:reference cpu', widget=SELECT_OR_ADD_OPTION_MULTIPLE("cpu").widget, label=T('CPU')),
    Field('image','upload', uploadfolder=uploadfolder),
    Field('thumbnail','upload', uploadfolder=uploadfolder, writable=False, readable=False),
    Field("slug", "string", compute=lambda row: format_slug(row.model, row.rev)),
    Field("id_ram", 'list:reference ram', widget=SELECT_OR_ADD_OPTION_MULTIPLE("ram").widget, label="RAM ID"),
    Field("ramsize", "integer", compute=lambda row: get_aggregate(row.id_ram, db.ram, 'mb'), label="RAM"),
    Field("id_flash", 'list:reference flash', widget=SELECT_OR_ADD_OPTION_MULTIPLE("flash").widget, label="Flash ID"),
    Field("flashsize", "integer", compute=lambda row: get_aggregate(row.id_flash, db.flash, 'mb'), label="Flash"),
    Field("note", "string"),
    Field("toh", "string", label="Table of Hardware"),
    Field("wikidevi", "string", label="Wikidevi.com"),
    Field("id_antenna", 'list:reference antenna', widget=SELECT_OR_ADD_OPTION_MULTIPLE("antenna").widget, label=T('Antenna')),
    Field("id_usb", 'list:reference usb', widget=SELECT_OR_ADD_OPTION_MULTIPLE("usb").widget, label=T('USB')),
    Field("id_serial", 'list:reference serial', widget=SELECT_OR_ADD_OPTION_MULTIPLE("serial").widget, label=T('Serial')),
    Field("id_wifi", 'list:reference wifi', widget=SELECT_OR_ADD_OPTION_MULTIPLE("wifi").widget, label=T('Wifi')),
    Field("id_network", 'list:reference network', widget=SELECT_OR_ADD_OPTION_MULTIPLE("network").widget, label=T('Network interfaces')),
    Field("id_firmware", 'list:reference firmware', widget=SELECT_OR_ADD_OPTION_MULTIPLE("firmware").widget, label=T('Firmware')),
    auth.signature,
)

# for creating thumbnails
box = (400, 300)
db.router.thumbnail.compute = lambda row: SMARTHUMB(row.image, box)


