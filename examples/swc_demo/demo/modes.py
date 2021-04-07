import autosar
from demo import packages, factory
from autosar.template.platform import AUTOSAR_Platform

class Mode:
    class BswM_ESH_Mode(autosar.Template):
        """ Mode Group Declaration """
        static_ref = packages.ModeDclrGroups.ref(None) + '/BswM_ESH_Mode'

        @classmethod
        def apply(cls, ws):
            name = cls.__name__
            ws.apply(packages.ModeDclrGroups)
            ws.apply(packages.DataTypes)
            modeDeclarationPackage = ws.find(packages.ModeDclrGroups.ref(ws))
            dataTypePackage = ws.find(packages.DataTypes.ref(ws))
            modeDeclarationGroup = modeDeclarationPackage.find(name)
            if modeDeclarationGroup is None:
                modeDeclarationGroup = modeDeclarationPackage.createModeDeclarationGroup(name,
                    [(0, "STARTUP"), (1, "RUN"), (2, "POSTRUN"), (3, "WAKEUP"), (4, "SHUTDOWN")], "STARTUP")

            if dataTypePackage.find(name) is None:
                ws.pushRoles()
                ws.setRole('/DataTypes/CompuMethods', 'CompuMethod')
                ws.setRole('/DataTypes/DataConstrs', 'DataConstraint')
                dataType = dataTypePackage.createImplementationDataTypeRef(name, AUTOSAR_Platform.ImplementationDataTypes.uint8.ref(ws),
                    valueTable = ['STARTUP', 'RUN', 'POSTRUN', 'WAKEUP', 'SHUTDOWN'])            
                mapping = modeDeclarationPackage.createDataTypeMappingSet(name + '_MappingSet')
                mapping.createModeRequestMapping(modeDeclarationGroup.ref, dataType.ref)
                ws.popRoles()

class Interface:
    BswM_ESH_Mode = factory.create_mode_switch_interface("BswM_MSI_ESH_Mode", Mode.BswM_ESH_Mode, "mode", is_service=True)

class Port:
    BswM_ESH_Mode = factory.create_mode_port_template('BswM_ESH_Mode', Interface.BswM_ESH_Mode)
