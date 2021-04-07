import sys
import autosar
import demo.modes as Modes
import demo.packages as Packages

class Demo1_swc(autosar.Template):
    @classmethod
    def apply(cls, ws):
        componentName = cls.__name__
        ws.apply(Packages.ComponentTypes)
        package = ws.find(Packages.ComponentTypes.ref(ws))
        if package.find(componentName) is None:
            swc = package.createApplicationSoftwareComponent(componentName)
            cls.addPorts(swc)
            cls.addBehavior(swc)

    @classmethod
    def addPorts(cls, swc):
        swc.apply(Modes.Port.BswM_ESH_Mode.Require)


    @classmethod
    def addBehavior(cls, swc):
        modeDisableList = [
            "BswM_ESH_Mode/POSTRUN",
            "BswM_ESH_Mode/SHUTDOWN",
            "BswM_ESH_Mode/STARTUP",
            "BswM_ESH_Mode/WAKEUP"
        ]
        swc_name = cls.__name__
        swc.behavior.appendDataTypeMappingRef('/ModeDclrGroups/BswM_ESH_Mode_MappingSet')
        swc.behavior.createRunnable(swc_name+'_Init')
        swc.behavior.createRunnable(swc_name+'_Exit')
        swc.behavior.createRunnable(swc_name+'_Run', portAccess = ['BswM_ESH_Mode'])
        swc.behavior.createTimerEvent(swc_name+'_Run', 1000, modeDependency = modeDisableList)
        swc.behavior.createModeSwitchEvent(swc_name+'_Init', 'BswM_ESH_Mode/RUN', activationType = 'ENTRY')
        swc.behavior.createModeSwitchEvent(swc_name+'_Exit', 'BswM_ESH_Mode/RUN', activationType = 'EXIT')