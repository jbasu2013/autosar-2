import autosar
from autosar.template.platform import AUTOSAR_Platform

class DataTypes(autosar.Template):
    """
    User-defined data types
    """
    static_ref = '/DataTypes'

    @classmethod
    def apply(cls, ws):
        package = ws.find(cls.ref(ws))
        if package is None:
            ws.apply(AUTOSAR_Platform)
            package=ws.createPackage(cls.__name__, role = 'DataType')
            package.createSubPackage('CompuMethods', role='CompuMethod')
            package.createSubPackage('DataConstrs', role='DataConstraint')
            package.createSubPackage('Units', role='Unit')

class Constants(autosar.Template):
    """
    User-defined constants
    """
    static_ref = '/Constants'
    @classmethod
    def apply(cls, ws):
        package = ws.find(cls.ref(ws))
        if package is None:            
            package=ws.createPackage(cls.__name__, role = 'Constant')

class PortInterfaces(autosar.Template):
    """
    User-defined port-interfaces
    """
    static_ref = '/PortInterfaces'
    @classmethod
    def apply(cls, ws):
        package = ws.find(cls.ref(ws))
        if package is None:        
            package=ws.createPackage(cls.__name__, role = 'PortInterface')

class ComponentTypes(autosar.Template):
    """
    User-defined port-interfaces
    """
    static_ref = '/ComponentTypes'
    @classmethod
    def apply(cls, ws):
        package = ws.find(cls.ref(ws))
        if package is None:            
            package=ws.createPackage(cls.__name__, role = 'ComponentType')

class ModeDclrGroups(autosar.Template):
    """
    Package for mode declaration groups
    """    
    static_ref = '/ModeDclrGroups'
    @classmethod
    def apply(cls, ws):        
        package = ws.find(cls.ref(ws))
        if package is None:            
            package=ws.createPackage(cls.__name__, role = 'ModeDclrGroup')