import sys
import autosar
import demo.modes as Modes
import demo.packages as Packages

class Demo2_swc(autosar.Template):
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
        pass

    @classmethod
    def addBehavior(cls, swc):
        swc_name = cls.__name__        
        swc.behavior.createRunnable(swc_name+'_Init')
        swc.behavior.createRunnable(swc_name+'_Run')        
        swc.behavior.createInitEvent(swc_name+'_Init')
        swc.behavior.createTimerEvent(swc_name+'_Run', 1000)