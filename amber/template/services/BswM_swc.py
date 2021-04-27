from autosar.template.platform import AUTOSAR_Platform
from amber.template.base import Amber
import autosar

class BswM_swc(autosar.Template):

    static_ref = '/Amber/ComponentTypes/BswM'

    @classmethod
    def apply(cls, ws):
        swc_name = "BswM"
        ws.apply(AUTOSAR_Platform)
        ws.apply(Amber)
        componentPackage = ws.find('/Amber/ComponentTypes')
        if componentPackage.find(swc_name) is None:
            modeDeclarationPackage = ws.find('/Amber/ModeDeclarations')
            interfacePackage = ws.find('/Amber/PortInterfaces')
            dataTypePackage = ws.find('/Amber/DataTypes')
            ws.pushRoles()
            ws.setRole('/Amber/DataTypes/CompuMethods', 'CompuMethod')
            ws.setRole('/Amber/DataTypes/DataConstraints', 'DataConstraint')

            dataTypePackage.createImplementationDataTypeRef('BswM_ESH_Mode', AUTOSAR_Platform.ImplementationDataTypes.uint8.ref(ws),
                valueTable = ['STARTUP', 'RUN', 'POSTRUN', 'WAKEUP', 'SHUTDOWN'])
            ws.popRoles()

            modeDeclarationGroup = modeDeclarationPackage.createModeDeclarationGroup('BswM_ESH_Mode',
            ["STARTUP", "RUN", "POST_RUN", "WAKEUP", "SHUTDOWN"], "STARTUP")

            interface = interfacePackage.createModeSwitchInterface('BswM_ESH_Mode_I',
            modeGroup = autosar.ModeGroup('ESH_Mode', modeDeclarationGroup.ref), isService = True)
            swc = componentPackage.createServiceComponent(swc_name)
            swc.createProvidePort('ESH_Mode', interface.ref)
            swc.behavior.createRunnable(swc_name+'_MainFunction', portAccess = ['ESH_Mode'])
            swc.behavior.createTimerEvent(swc_name+'_MainFunction', 100)









