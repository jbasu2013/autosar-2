import autosar
import demo.packages as packages
from autosar.template.platform import AUTOSAR_Platform

_data_type_root = '/DataTypes'

def _find_item_by_index(item, index):
    if isinstance(item, str):
        retval = index
    elif isinstance(item, tuple):
        if len(item)==2:
            retval = item[0]
        elif len(item)==3:
            retval = item[1]
        else:
            raise RuntimeError('unexptected length in tuple')
    else:
        raise NotImplementedError(type(item))
    return retval

#### Data Types
def create_enumeration_impl_type(name, value_table, type_class = AUTOSAR_Platform.BaseTypes.uint8):
    static_ref = packages.DataTypes.ref(None) + '/' + name

    first_index = 0
    last_index = len(value_table)-1
    lower_limit = _find_item_by_index(value_table[first_index], first_index)
    upper_limit = _find_item_by_index(value_table[last_index], last_index)

    @classmethod
    def apply(cls, ws):
        ws.apply(packages.DataTypes)
        package = ws.find(packages.DataTypes.ref(ws))
        if package.find(cls.__name__) is None:
            ws.apply(cls.type_class)
            package.createImplementationDataType(cls.__name__, cls.type_class.ref(ws), valueTable=cls.value_table)

    return type(name, (autosar.Template,), dict(lower_limit = lower_limit,
                                                upper_limit = upper_limit,
                                                value_table = value_table,
                                                static_ref = static_ref,
                                                type_class = type_class,
                                                apply=apply))

def create_enumeration_impl_ref_type(name, value_table, type_class = AUTOSAR_Platform.ImplementationDataTypes.uint8):
    static_ref = packages.DataTypes.ref(None) + '/' + name

    first_index = 0
    last_index = len(value_table)-1
    lower_limit = _find_item_by_index(value_table[first_index], first_index)
    upper_limit = _find_item_by_index(value_table[last_index], last_index)

    @classmethod
    def apply(cls, ws):
        ws.apply(packages.DataTypes)
        package = ws.find(packages.DataTypes.ref(ws))
        if package.find(cls.__name__) is None:
            ws.apply(cls.type_class)
            package.createImplementationDataTypeRef(cls.__name__, cls.type_class.ref(ws), valueTable=cls.value_table)

    return type(name, (autosar.Template,), dict(lower_limit = lower_limit,
                                                upper_limit = upper_limit,
                                                value_table = value_table,
                                                static_ref = static_ref,
                                                type_class = type_class,
                                                apply=apply))
def create_physical_uint8_type(name, lower_limit, upper_limit, offset, scaling, unit,
         invalid_range_start = None, error_range_start = None, not_available_range_start=None):
    return create_physical_type(name, packages.AUTOSAR_Platform.BaseTypes.uint8,
        lower_limit,
        upper_limit,
        offset,
        scaling,
        unit,
        invalid_range_start,
        error_range_start,
        not_available_range_start)

def create_physical_uint16_type(name, lower_limit, upper_limit, offset, scaling, unit,
         invalid_range_start = None, error_range_start = None, not_available_range_start=None):
    return create_physical_type(name, AUTOSAR_Platform.BaseTypes.uint16,
        lower_limit,
        upper_limit,
        offset,
        scaling,
        unit,
        invalid_range_start,
        error_range_start,
        not_available_range_start)

def create_physical_uint32_type(name, lower_limit, upper_limit, offset, scaling, unit,
         invalid_range_start = None, error_range_start = None, not_available_range_start=None):
    return create_physical_type(name, AUTOSAR_Platform.BaseTypes.uint32,
        lower_limit,
        upper_limit,
        offset,
        scaling,
        unit,
        invalid_range_start,
        error_range_start,
        not_available_range_start)

def create_physical_type(name, type_class, lower_limit, upper_limit, offset, scaling, unit,
         invalid_range_start = None, error_range_start = None, not_available_range_start=None):

    @classmethod
    def ref(cls, ws):
        return packages.DataTypes.ref(ws) + '/' + cls.__name__

    @classmethod
    def apply(cls, ws):
        ws.apply(packages.DataTypes)
        package = ws.find(packages.DataTypes.ref(ws))
        if package.find(cls.__name__) is None:
            ws.apply(cls.type_class)
            package.createImplementationDataType(cls.__name__, cls.type_class.ref(ws),
                lowerLimit = cls.lower_limit,
                upperLimit = cls.upper_limit
                )

    return type(name, (autosar.Template,), dict(lower_limit = lower_limit,
                                                upper_limit = upper_limit,
                                                offset = offset,
                                                scaling = scaling,
                                                unit = unit,
                                                invalid_range_start = invalid_range_start,
                                                error_range_start = error_range_start,
                                                not_available_range_start = not_available_range_start,
                                                type_class = type_class,
                                                ref=ref,
                                                apply=apply))

### Constants

def create_constant_from_value_table(name, class_with_vt, index = None):
    value_table = class_with_vt.value_table
    static_ref = packages.Constants.ref(None) + '/' + name

    if index is None:
        #By default, choose the last value_table entry as init_value
        index = len(value_table)-1

    @classmethod
    def ref(cls, ws):
        return packages.Constants.ref(ws) + '/' + cls.__name__

    @classmethod
    def apply(cls, ws):
        ws.apply(packages.Constants)
        package = ws.find(packages.Constants.ref(ws))
        if package.find(cls.__name__) is None:
            ws.apply(class_with_vt)
            package.createConstant(cls.__name__, cls.type_class.ref(ws), cls.value )

    return type(name, (autosar.Template,), dict(value = value_table[index],
                                                type_class = class_with_vt,
                                                static_ref = static_ref,
                                                apply=apply))

def create_constant_from_upper_limit(name, class_with_limits):

    static_ref = packages.Constants.ref(None) + '/' + name

    @classmethod
    def apply(cls, ws):
        ws.apply(packages.Constants)
        package = ws.find(packages.Constants.ref(ws))
        if package.find(cls.__name__) is None:
            ws.apply(class_with_limits)
            package.createConstant(cls.__name__, cls.type_class.ref(ws),
            cls.type_class.upper_limit)

    return type(name, (autosar.Template,), dict(type_class = class_with_limits,
                                                static_ref = static_ref,
                                                apply=apply))

# Port Interfaces

def create_sender_receiver_interface(name, type_template, element_name = None, is_service = False):
    assert(issubclass(type_template, autosar.Template))
    if element_name is None:
        element_name = name
        if element_name[-2:]=='_I':
            element_name=element_name[:-2]

    static_ref = packages.PortInterfaces.ref(None) + '/' + name

    @classmethod
    def apply(cls, ws):
        ws.apply(packages.PortInterfaces)
        package = ws.find(packages.PortInterfaces.ref(ws))
        if package.find(name) is None:
            ws.apply(cls.type_class)
            package.createSenderReceiverInterface(name, autosar.DataElement(cls.element_name,
            cls.type_class.__name__),
            isService = cls.is_service,)
    return type(name, (autosar.Template,), dict(type_class = type_template,
                                                element_name = element_name,
                                                static_ref = static_ref,
                                                is_service = is_service,
                                                apply=apply))

def create_mode_switch_interface(name, mode_declaration_group, mode_name, is_service = False):

    static_ref = packages.PortInterfaces.ref(None) + '/' + name

    @classmethod
    def apply(cls, ws):
        ws.apply(packages.PortInterfaces)
        package = ws.find(packages.PortInterfaces.ref(ws))
        if package.find(cls.__name__) is None:
            ws.apply(cls.mode_declaration_group)
            package.createModeSwitchInterface(cls.__name__,
                modeGroup=autosar.ModeGroup(cls.mode_name,
                cls.mode_declaration_group.ref(ws)),
                isService=cls.is_service)

    return type(name, (autosar.Template,), dict(mode_declaration_group = mode_declaration_group,
                                                mode_name = mode_name,
                                                is_service = is_service,
                                                static_ref=static_ref,
                                                apply=apply))

# Ports
def _createProvidePortHelper(swc, name, port_interface_class, init_value_class = None):
    ws = swc.rootWS()
    if swc.find(name) is None:
        ws.apply(port_interface_class)
        if init_value_class is not None:
            ws.apply(init_value_class)
            swc.createProvidePort(name,
                port_interface_class.ref(ws),
                initValueRef = init_value_class.ref(ws))
        else:
            swc.createProvidePort(name, port_interface_class.ref(ws))

def _createRequirePortHelper(swc, name, port_interface_class, init_value_class = None, alive_timeout = None):
    ws = swc.rootWS()
    if swc.find(name) is None:
        ws.apply(port_interface_class)
        if init_value_class is not None:
            ws.apply(init_value_class)
            swc.createRequirePort(name,
                port_interface_class.ref(ws),
                initValueRef = init_value_class.ref(ws), aliveTimeout = alive_timeout)
        else:
            swc.createRequirePort(name, port_interface_class.ref(ws), aliveTimeout = alive_timeout)

def _createModeProvidePortHelper(swc, name, port_interface_class):
    ws = swc.rootWS()
    if swc.find(name) is None:
        ws.apply(port_interface_class)
        swc.createProvidePort(name, port_interface_class.ref(ws))

def _createModeRequirePortHelper(swc, name, port_interface_class):
    ws = swc.rootWS()
    if swc.find(name) is None:
        ws.apply(port_interface_class)
        swc.createRequirePort(name, port_interface_class.ref(ws))

def _createProvidePortTemplate(inner_class_name, outer_class_name, port_interface_class, init_value_class=None):
    @classmethod
    def apply(cls, swc):
        _createModeProvidePortHelper(swc, cls.name, cls.port_interface)
    return type(inner_class_name, (autosar.Template,),
            dict(   name=outer_class_name,
                    port_interface=port_interface_class,
                    init_value=init_value_class,
                    apply=apply
                ))

def _createRequirePortTemplate(inner_class_name, outer_class_name, port_interface_class, init_value_class=None, alive_timeout = None):
    @classmethod
    def apply(cls, swc):
        _createRequirePortHelper(swc, cls.name, cls.port_interface, cls.init_value, cls.alive_timeout)
    return type(inner_class_name, (autosar.Template,),
            dict(   name=outer_class_name,
                    port_interface=port_interface_class,
                    init_value=init_value_class,
                    alive_timeout=alive_timeout,
                    apply=apply
                ))

def _createModeProvidePortTemplate(inner_class_name, outer_class_name, port_interface_class):
    @classmethod
    def apply(cls, swc):
        _createProvidePortHelper(swc, cls.name, cls.port_interface)
    return type(inner_class_name, (autosar.Template,),
            dict(   name=outer_class_name,
                    port_interface=port_interface_class,
                    apply=apply
                ))

def _createModeRequirePortTemplate(inner_class_name, outer_class_name, port_interface_class):
    @classmethod
    def apply(cls, swc):
        _createModeRequirePortHelper(swc, cls.name, cls.port_interface)
    return type(inner_class_name, (autosar.Template,),
            dict(   name=outer_class_name,
                    port_interface=port_interface_class,
                    apply=apply
                ))

def create_client_server_port_template(name, port_interface_class):
    return type(name, (), dict(Call=_createRequirePortTemplate('Call', name, port_interface_class),
                               Require=_createRequirePortTemplate('Require', name, port_interface_class),
                               Serve=_createProvidePortTemplate('Serve', name, port_interface_class),
                             Provide=_createProvidePortTemplate('Provide', name, port_interface_class)))

def create_mode_port_template(name, port_interface_class):
    return type(name, (), dict(Require=_createModeRequirePortTemplate('Require', name, port_interface_class),
                              Provide=_createModeProvidePortTemplate('Provide', name, port_interface_class)))

def create_sender_receiver_port_template(name, port_interface_class, init_value_class = None, alive_timeout = None):
    return type(name, (), dict(Provide=_createProvidePortTemplate('Provide', name, port_interface_class, init_value_class),
                                Send=_createProvidePortTemplate('Send', name, port_interface_class, init_value_class),
                                Require=_createRequirePortTemplate('Require', name, port_interface_class, init_value_class, alive_timeout),
                                Receive=_createRequirePortTemplate('Receive', name, port_interface_class, init_value_class, alive_timeout)))