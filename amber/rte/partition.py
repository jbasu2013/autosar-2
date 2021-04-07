import sys
import autosar.component
from collections import namedtuple
import amber.rte.base

TARGET_TYPE_COMPONENT = 0
TARGET_TYPE_IMPLEMENTATION_DATATYPE = 1
TARGET_TYPE_MODE_DECLARATION_GROUP = 2


class Partition:
    """
    A container where software components can be instantiated from component prototypes
    """
    def __init__(self, ws):
        self.componentTable = {} #Component instances
        self.dataTypeTable = {}
        self.applicationDataTypeTable = {}
        self.modeGroupTable = {}        
        assert(isinstance(ws, autosar.Workspace))
        self.ws = ws
        self.next_id = 0

    def toDict(self):
        result = {'componentList': [],
            'dataTypeTable': {},
            'applicationDataTypeTable': {},
            'modeGroupTable': {},
        }
        for key in sorted(self.componentTable.keys()):
            componentInstance = self.componentTable[key]
            result['componentList'].append(componentInstance.toDict())
        for key, dataTypeInstance in self.dataTypeTable.items():
            result['dataTypeTable'][key] = dataTypeInstance.toDict()
        for key, modeGroupInstance in self.modeGroupTable.items():
            result['modeGroupTable'][key] = modeGroupInstance.toDict()
        return result

    def createComponent(self, protoRef, instance_name=None):
        """
        Create an instance from a component prototype reference.
        By default, the instance name will be idential to the prototype name.
        Use optional argument instance_name to override the selected name.
        All component instances must have a unique name within current RTE partition.
        """
        self._apply(protoRef, TARGET_TYPE_COMPONENT, instance_name)

    def createConnector(self, portRef1, portRef2):
        """
        creates a connector between two ports
        """
        assert (self.ws is not None)
        port1  = self.findPort(portRef1)
        port2 = self.findPort(portRef2)
        if port1 is None:
            raise autosar.base.InvalidPortRef(portRef1)
        if port2 is None:
            raise autosar.base.InvalidPortRef(portRef2)

        portProtoType1 = port1.portPrototype
        portProtoType2 = port2.portPrototype
        providePort=None
        requirePort=None        
        if isinstance(portProtoType1, autosar.port.RequirePort) and isinstance(portProtoType2, autosar.port.ProvidePort):
            requirePort, providePort = port1, port2
        elif isinstance(portProtoType1, autosar.port.ProvidePort) and isinstance(portProtoType2, autosar.port.RequirePort):
            providePort, requirePort = port1, port2
        elif isinstance(portProtoType1, autosar.port.RequirePort) and isinstance(portProtoType2, autosar.port.RequirePort):
            raise ValueError('cannot create assembly connector between two require ports')
        else:
            raise ValueError('cannot create assembly connector between two provide ports')
        self._createConnectorInternal(providePort, requirePort)
    
    def findPort(self, portRef):
        parts = autosar.base.splitRef(portRef)
        if len(parts) == 2:
            componentName, portName = parts[0], parts[1]
            componentInstance = self.componentTable.get(componentName, None)
            if componentInstance is not None:
                return componentInstance.findPortInstance(portName)
        else:
            raise autosar.base.InvalidReference(portRef)
        return None

#    def autoConnect(self):
#       """
#       Attemts to create compatible connectors between components
#       """
#       require_port_list = [] #list of RequirePort
#       provide_port_list = [] #list of ProvidePort
#       for rte_comp in self.components:
#          for rte_port in rte_comp.requirePorts:
#             require_port_list.append(rte_port)
#          for rte_port in rte_comp.providePorts:
#             provide_port_list.append(rte_port)

#       for require_port in require_port_list:
#          provide_port = self._findCompatibleProvidePort(require_port, provide_port_list)
#          if provide_port is not None:
#             self._createConnectorInternal(provide_port, require_port)

#    def unconnectedPorts(self):
#       """
#       Returns a generator that yields all unconnected ports of this partition
#       """
#       for component in self.components:
#          for port in component.requirePorts+component.providePorts:
#             if len(port.connectors)==0:
#                yield port

    def _apply(self, reference, targetType, name = None):
        """
        Given the reference string, create an instance of an object using the referenced prototype
        """
        prototype = self.ws.find(reference)
        if prototype is None:
            if targetType == TARGET_TYPE_COMPONENT:
                raise autosar.base.InvalidComponentTypeRef(reference)
            elif targetType == TARGET_TYPE_IMPLEMENTATION_DATATYPE:
                raise autosar.base.InvalidImplementationDataType(reference)
            elif targetType == TARGET_TYPE_MODE_DECLARATION_GROUP:
                raise autosar.base.InvalidModeDeclarationGroupRef(reference)
            else:
                raise autosar.base.InvalidReference(reference)
        if isinstance(prototype, autosar.component.ComponentType):
            swc_name = name if name is not None else prototype.name
            if swc_name in self.componentTable:
                print("A component with name {} has already been created in this partition".format(swc_name))
            self._createComponentInstance(prototype, swc_name)
        elif isinstance(prototype, autosar.mode.ModeDeclarationGroup):
            if reference not in self.modeGroupTable:
                self._createModeGroupInstance(prototype)
        elif isinstance(prototype, autosar.datatype.ImplementationDataType):
            if reference not in self.dataTypeTable:
                self._createImplementationDataTypeInstance(prototype)
        else:
            raise NotImplementedError(type(prototype))        
        return prototype

    def _incrementId(self):
        retval = self.next_id
        self.next_id += 1
        return retval

    def _createComponentInstance(self, swc_prototype, swc_name):
        """
        Creates a ComponentInstance from prototype swc
        """
        if swc_name in self.componentTable:
            print("A component with name {} already exists in the partition", file = sys.stderr)
            return
        if isinstance(swc_prototype, (autosar.component.AtomicSoftwareComponent)):
            componentInstance = self._createAtomicComponentInstance(swc_prototype, swc_name)
        else:
            print("Unsupported component type: " + str(type(swc_prototype)), file=sys.stderr)
        self.componentTable[swc_name] = componentInstance

    def _createAtomicComponentInstance(self, componentPrototype, name):
        if isinstance(componentPrototype, (autosar.component.ApplicationSoftwareComponent)):
            componentInstance = amber.rte.base.ApplicationSoftwareComponentInstance(componentPrototype, name)
        elif isinstance(componentPrototype, (autosar.component.ServiceComponent)):
            componentInstance = amber.rte.base.ServiceComponentInstance(componentPrototype, name)
        else:
            raise NotImplementedError(str(type(componentPrototype)))
        for portPrototype in componentPrototype.requirePorts + componentPrototype.providePorts:
            self._createPortInstances(componentInstance, portPrototype)
        self._processComponentBehavior(componentInstance, componentPrototype.behavior)
        return componentInstance

    def _createPortInstances(self, componentInstance, portPrototype):
        assert(self.ws is not None)
        portInterface = self.ws.find(portPrototype.portInterfaceRef)
        if portInterface is None:
            raise autosar.base.InvalidPortInterfaceRef(portPrototype.portInterfaceRef)
        if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            raise NotImplementedError('SenderReceiver')
        elif isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
            modeGroupPrototype = portInterface.modeGroup
            self._apply(modeGroupPrototype.typeRef, TARGET_TYPE_MODE_DECLARATION_GROUP)
            isProvidePort = True if isinstance(portPrototype, autosar.port.ProvidePort) else False
            portInstance = amber.rte.base.ModePortInstance(portPrototype, modeGroupPrototype, isProvidePort, self._incrementId())
        else:
            raise NotImplementedError(str(type(portInterface)))
        componentInstance.insertPortInstance(portInstance)

    def _createModeGroupInstance(self, modeDeclarationGroup):
        if modeDeclarationGroup.initialModeRef is not None:
            initialMode = self.ws.find(modeDeclarationGroup.initialModeRef)
            if initialMode is None:
                raise autosar.base.InvalidModeDeclarationRef(modeDeclarationGroup.initialModeRef)
            initialModeName = initialMode.name
        else:
            initialModeName = None
        modeGroupInstance = amber.rte.base.ModeGroupInstance(modeDeclarationGroup.name, initialModeName)
        for modeDeclaration in modeDeclarationGroup.modeDeclarations:
            modeInstance = amber.rte.base.ModeInstance(modeDeclaration.name, modeDeclaration.value)
            modeGroupInstance.modeTable[modeDeclaration.name] = modeInstance
        self.modeGroupTable[modeDeclarationGroup.ref] = modeGroupInstance

    def _processComponentBehavior(self, componentInstance, behavior):
        self._processDataTypeMappingRefs(componentInstance, behavior)
        self._processRunnables(componentInstance, behavior)
    
    def _processDataTypeMappingRefs(self, componentInstance, behavior):
        for dataTypeMappingRef in behavior.dataTypeMappingRefs:
            dataTypeMapping = self.ws.find(dataTypeMappingRef)
            if dataTypeMapping is None:
                raise autosar.base.InvalidDataTypeMappingRef(dataTypeMappingRef)
            self._processDataTypeMapping(componentInstance, dataTypeMapping)

    def _processDataTypeMapping(self, componentInstance, dataTypeMappingSet):
        assert(isinstance(dataTypeMappingSet, autosar.datatype.DataTypeMappingSet))
        for modeDeclarationGroupRef in dataTypeMappingSet.modeRequestMap:
            implementationDataTypeRef = dataTypeMappingSet.findMappedModeRequestRef(modeDeclarationGroupRef)
            self._apply(implementationDataTypeRef, TARGET_TYPE_IMPLEMENTATION_DATATYPE)
#            modeGroupInstance = self.modeGroupTable.get(modeDeclarationGroupRef, None)
#            if modeGroupInstance is not None:
#                pass
#                #print("{} Used by {}".format(modeDeclarationGroupRef, componentInstance.name))

    def _processRunnables(self, componentInstance, behavior):
        for runnable in behavior.runnables:
            runnableInstance = amber.rte.base.RunnableInstance(runnable, componentInstance, self._incrementId())
            componentInstance.insertRunnable(runnableInstance)

    def _createImplementationDataTypeInstance(self, prototype):
        assert(isinstance(prototype, autosar.datatype.ImplementationDataType))
        attributes = self._resolve_implementattion_type_attributes(prototype)
        attributes.id = self._incrementId()
        instance = amber.rte.base.ImplementationTypeInstance(attributes)
        instance.ref = prototype.ref
        self.dataTypeTable[prototype.ref] = instance

    def _resolve_implementattion_type_attributes(self, dataType):
        attributes = amber.rte.base.DataTypeAttributes(dataType.name)
        implementationTypeRef = dataType.implementationTypeRef
        baseTypeRef = dataType.baseTypeRef
        dataConstraintRef = dataType.dataConstraintRef
        compuMethodRef = dataType.compuMethodRef
        baseType = self.ws.find(baseTypeRef) if baseTypeRef is not None else None
        if implementationTypeRef is not None:
            targetImplementationType = self._apply(implementationTypeRef, TARGET_TYPE_IMPLEMENTATION_DATATYPE)
        else:
            targetImplementationType = None
        dataConstraint = self.ws.find(dataConstraintRef) if dataConstraintRef is not None else None
        compuMethod = self.ws.find(compuMethodRef) if compuMethodRef is not None else None
        arraySize = dataType.arraySize
        typeEmitter = dataType.typeEmitter
        if baseType is None and baseTypeRef is not None:
            raise autosar.base.InvalidDataTypeRef(baseTypeRef)
        if dataConstraint is None and dataConstraintRef is not None:
            raise autosar.base.InvalidDataConstraintRef(baseTypeRef)
        if compuMethod is None and compuMethodRef is not None:
            raise autosar.base.InvalidCompuMethodRef(baseTypeRef)

        if targetImplementationType is not None:
           attributes.targetType = targetImplementationType
        if typeEmitter is not None:
            if typeEmitter.upper() != 'RTE':
                attributes.skipGeneration = True
        return attributes


#    def _analyzePortRef(self, portRef):
#       parts=autosar.base.splitRef(portRef)
#       if len(parts)==2:
#          #assume format 'componentName/portName' with ComponentType role set
#          port=None
#          for component in self.components:
#             if component.name == parts[0]:
#                for port in component.requirePorts + component.providePorts:
#                   if parts[1] == port.name:
#                      return port
#       return None

    def _createConnectorInternal(self, providePortInstance, requirePortInstance):
        providePortInstance.requirePortConnectorList.append(requirePortInstance)
        requirePortInstance.providePortConnectorList.append(providePortInstance)
#      if connectorName in self.assemblyConnectorMap:
#         raise ValueError('connector "%s" already exists'%connectorName)
#      self.assemblyConnectorMap[connectorName]=(provide_port,require_port)
#      provide_port.connectors.append(require_port)
#      require_port.connectors.append(provide_port)

#    def _findCompatibleProvidePort(self, require_port, provide_port_list):
#       require_port_interface = self.ws.find(require_port.ar_port.portInterfaceRef)
#       if require_port_interface is None: raise ValueError("Invalid port interface ref: %s"%require_port.ar_port.portInterfaceRef)
#       for provide_port in provide_port_list:
#          provide_port_interface = self.ws.find(provide_port.ar_port.portInterfaceRef)
#          if provide_port_interface is None: raise ValueError("Invalid port interface ref: %s"%provide_port.ar_port.portInterfaceRef)
#          if require_port_interface==provide_port_interface and (require_port.ar_port.name == provide_port.ar_port.name):
#             return provide_port
#       return None
