import autosar.base
import autosar.datatype
import autosar.portinterface
import collections
import cfile as C

class Instance:
   """
   Base class for all instances
   """
   def __init__(self, name, id):
      self.name = name
      self.id = id

class ModeGroupInstance(Instance):
    def __init__(self, name, initialModeName, id = None):
        super().__init__(name, id)
        self.modeTable = {} #Dictionary of ModeInstance objects
        self.initialModeName = initialModeName
        self.dataTypeMappingTable = {} #Key: SWC reference. Value: ImplementationDataTypeInstance

    def toDict(self):
        result = {'ModeGroupName': self.name, 'ModeTable':{}}
        if self.initialModeName is not None:
            result['InitialModeName'] = self.initialModeName
        for key, value in self.modeTable.items():
            result['ModeTable'][key]=value.toDict()
        return result

    def find(self, modeName):
        return self.modeTable.get(modeName, None)

class ModeInstance(Instance):
    def __init__(self, name, value = None, id = None):
        super().__init__(name, id)
        self.value = value

    def toDict(self):
        result = {'ModeName': self.name}
        if self.value is not None:
            result['Value'] = self.value
        return result

class ComponentInstance:
    def __init__(self, name, componentPrototype):
        self.name = name
        self.componentPrototype = componentPrototype
        self.portTable = {} #Key is port name, value is a port instance
        self.runnableTable = {}

    def toDict(self):
        result = {'name': self.name,
            'componentPrototypeRef': self.componentPrototype.ref,
            'runnableList': []}
        modePorts = []
        for key in sorted(self.portTable.keys()):
            portInstance = self.portTable[key]
            if isinstance(portInstance, ModePortInstance):
                modePorts.append(portInstance.toDict())
            else:
                raise NotImplementedError(str(type(portInstance)))
        if len(modePorts) > 0:
            result['modePorts'] = modePorts
        for name in sorted(self.runnableTable.keys()):
            runnableInstance = self.runnableTable[name]
            result['runnableList'].append(runnableInstance.toDict())
        return result

    def insertPortInstance(self, portInstance):
        assert(portInstance.name not in self.portTable)
        portInstance.parent = self
        self.portTable[portInstance.name] = portInstance

    def findPortInstance(self, portName):
        return self.portTable.get(portName, None)

    def findPortPrototype(self, portName):
        portInstance = self.portTable.get(portName, None)
        if portInstance is not None:
            return portInstance.portPrototype
        return None

    def findRunnableInstance(self, runnableName):
        return self.runnableTable.get(runnableName, None)

    def insertRunnable(self, runnableInstance):
        assert(isinstance(runnableInstance, RunnableInstance))
        assert(runnableInstance.name not in self.runnableTable)
        self.runnableTable[runnableInstance.name] = (runnableInstance)




class ApplicationSoftwareComponentInstance(ComponentInstance):
    def __init__(self, prototype, name = None):
        super().__init__(name, prototype)

class ServiceComponentInstance(ComponentInstance):
    def __init__(self, prototype, name = None):
        super().__init__(name, prototype)

ImplementationTypeAttributes = collections.namedtuple('ImplementationTypeAttributes', ['baseType',
'implementationType', 'dataConstraint', 'compuMethod', 'arraySize', 'typeEmitter'])

BaseTypeAttributes = collections.namedtuple('BaseTypeAttributes', ['baseTypeSize', 'baseTypeEncoding', 'nativeDeclaration'])

class DataTypeAttributes:
    def __init__(self, name):
        self.name = str(name)
        self.targetType = None
        self.id = None
        self.skipGeneration = False


class ImplementationTypeInstance(Instance):
    def __init__(self, attr):
        assert(isinstance(attr, DataTypeAttributes))
        super().__init__(attr.name, attr.id)
        self.targetType = attr.targetType
        self.skipGeneration = attr.skipGeneration
        self._ref = None

    @property
    def ref(self):
        return self._ref
    @ref.setter
    def ref(self, value):
        self._ref=str(value)

    def toDict(self):
        result = {'name': self.name,
            'skipGeneration' : self.skipGeneration
        }
        if self.id is not None:
            result['$id']= self.id
        if self.targetType is not None:
            result['targetTypeRef']= self.targetType.ref
        return result

# class ImplementationTypeInstance2:
#     def __init__(self, dataType):
#         ws = dataType.rootWS()
#         if ws is None:
#             raise RuntimeError("Root workspace not found")
#         if isinstance(dataType, autosar.datatype.ImplementationDataType):
#             attribute_stack = self._resolve_references(ws, dataType)
#             self.name = dataType.name
#             self.sourceRef = dataType.ref
#             self.baseType = self._find_type_attribute(attribute_stack, 'baseType')
#             self.implementationType = self._find_type_attribute(attribute_stack, 'implementationType')
#             self.dataConstraint = self._find_type_attribute(attribute_stack, 'dataConstraint')
#             self.compuMethod = self._find_type_attribute(attribute_stack, 'compuMethod')
#             self.arraySize = self._find_type_attribute(attribute_stack, 'arraySize')
#             self.typeEmitter = self._find_type_attribute(attribute_stack, 'typeEmitter')
#         else:
#             raise NotImplementedError(type(dataType))

#     def _resolve_references(self, ws, dataType):
#         stack = []
#         elem = dataType
#         while elem is not None:
#             if isinstance(elem, autosar.datatype.ImplementationDataType):
#                 implementationTypeRef = elem.implementationTypeRef
#                 baseTypeRef = elem.baseTypeRef
#                 dataConstraintRef = elem.dataConstraintRef
#                 compuMethodRef = elem.compuMethodRef
#                 baseType = ws.find(baseTypeRef) if baseTypeRef is not None else None
#                 implementationType = ws.find(implementationTypeRef) if implementationTypeRef is not None else None
#                 dataConstraint = ws.find(dataConstraintRef) if dataConstraintRef is not None else None
#                 compuMethod = ws.find(compuMethodRef) if compuMethodRef is not None else None
#                 arraySize = dataType.arraySize
#                 typeEmitter = dataType.typeEmitter
#                 if baseType is None and baseTypeRef is not None:
#                     raise autosar.base.InvalidDataTypeRef(baseTypeRef)
#                 if implementationType is None and implementationTypeRef is not None:
#                     raise autosar.base.InvalidDataTypeRef(baseTypeRef)
#                 if dataConstraint is None and dataConstraintRef is not None:
#                     raise autosar.base.InvalidDataConstraintRef(baseTypeRef)
#                 if compuMethod is None and compuMethodRef is not None:
#                     raise autosar.base.InvalidCompuMethodRef(baseTypeRef)
#                 stack.append(ImplementationTypeAttributes(baseType, implementationType, dataConstraint, compuMethod, arraySize, typeEmitter))

#                 #Decide where to traverse next
#                 if baseType is not None and implementationType is not None:
#                     #TODO: Do we need to support multiple inheritance in AUTOSAR?
#                     raise NotImplementedError("Data type uses multiple inheritance")
#                 if baseType is not None:
#                     elem = baseType
#                 elif implementationType is not None:
#                     elem = implementationType
#                 else:
#                     elem = None
#             else:
#                 baseTypeSize = elem.size
#                 baseTypeEncoding = elem.typeEncoding
#                 nativeDeclaration = elem.nativeDeclaration
#                 stack.append(BaseTypeAttributes(baseTypeSize, baseTypeEncoding, nativeDeclaration))
#                 elem = None
#         return stack

#     def _find_type_attribute(self, attribute_stack, name):
#         for attributes in attribute_stack:
#             if hasattr(attributes, name):
#                 attr = getattr(attributes, name)
#                 if attr is not None:
#                     return attr
#         return None

class PortInstance(Instance):
    def __init__(self, portPrototype, isProvidePort, isProvideRequirePort = False, id = None):
        super().__init__(portPrototype.name, id)
        self.parent = None
        self.portPrototype = portPrototype
        self.isProvidePort = isProvidePort
        self.isProvideRequirePort = isProvideRequirePort #Reserved for future use
        if isProvidePort:
            self.requirePortConnectorList = []
            self.providePortConnectorList = None
        else:
            self.requirePortConnectorList = None
            self.providePortConnectorList = []

class SenderReceiverPortInstance(PortInstance):
    def __init__(self, portPrototype, dataElementPrototype, isProvidePort, id = None):
        super().__init__(portPrototype, isProvidePort, False, id)
        self.dataElementPrototype = dataElementPrototype

class ParameterPortInstance(PortInstance):
    def __init__(self, portPrototype, parameterDataPrototype, isProvidePort, id = None):
        super().__init__(portPrototype, isProvidePort, False, id)
        self.parameterDataPrototype = parameterDataPrototype

class ClientServerPortInstance(PortInstance):
    def __init__(self, portPrototype, operationPrototype, isProvidePort, id = None):
        super().__init__(portPrototype, isProvidePort, False, id)
        self.operationPrototype = operationPrototype

class ModePortInstance(PortInstance):
    def __init__(self, portPrototype, modeGroupPrototype, isProvidePort, id = None):
        super().__init__(portPrototype, isProvidePort, False, id)
        self.modeGroupPrototype = modeGroupPrototype

    def toDict(self):
        result = {'name': self.name,
            'portProtoTypeRef': self.portPrototype.ref,
            'modeGroupPrototypeRef': self.modeGroupPrototype.ref,
            'isProvidePort': self.isProvidePort,
            '$id': self.id,
        }
        if self.isProvidePort:
            connectorList = []
            for requirePortInstance in self.requirePortConnectorList:
                connectorList.append('{0.parent.name}/{0.name}'.format(requirePortInstance))
            result['requirePortConnectorList'] = connectorList
        else:
            connectorList = []
            for providePortInstance in self.providePortConnectorList:
                connectorList.append('{0.parent.name}/{0.name}'.format(providePortInstance))
            result['providePortConnectorList'] = connectorList
        return result

class DataElementAttributes:
    """
    Used by SenderReceiverPortInstance
    """
    pass

class ModeGroupAttributes:
    """
    Used by ModePortInstance
    """
    pass

class ParameterDataAttributes:
    """
    Used by ParameterPortInstance
    """
    pass

class OperationAttributes:
    """
    Used by ClientServerPortInstance
    """
    pass

class RunnableInstance(Instance):
    """
    RTE Runnable
    """
    def __init__(self, runnablePrototype, parent, id = None):
        super().__init__(runnablePrototype.name, id)
        self.parent = parent
        self.runnablePrototype = runnablePrototype
        self.name = runnablePrototype.name
        self.symbol = runnablePrototype.symbol
        self.functionPrototype = C.function(self.symbol, 'void')
        self.dataElementAccessList=[]
        self.operationAccessList=[]
        self.triggerList=[]

    def toDict(self):
        result = {'name': self.name, '$id': self.id }
        if len(self.triggerList) > 0:
             result['triggerList']=[]
             for trigger in self.triggerList:
                 result['triggerList'].append(trigger.toDict())
        return result

    def insertEvent(self, eventTrigger):
        self.triggerList.append(eventTrigger)

class ModeSwitchEventTrigger(Instance):
    def __init__(self, event, modeProvidePort, modeGroupInstance, id = None):
        super().__init__(None, id)
        modeInstRef = event.modeInstRef.modeDeclarationRef
        parts = autosar.base.splitRef(modeInstRef)
        self.modeInstance = modeGroupInstance.find(parts[-1])
        if self.modeInstance is None:
            raise ValueError("Unrecognized mode name detected: "+parts[-1])
        self.modeProvidePort = modeProvidePort
        self.modeGroupInstance = modeGroupInstance
        if event.activationType == 'ON-ENTRY':
            self.activationType = 'OnEntry'
        elif event.activationType == 'ON-EXIT':
            self.activationType = 'OnExit'
        else:
            raise RuntimeError('Event activationType must either be "ON-ENTRY" or "ON-EXIT"')
        self.name = '_'.join([modeProvidePort.parent.name, modeProvidePort.name, modeGroupInstance.name, self.modeInstance.name])


    def toDict(self):
        result = {'$id': self.id, 'triggerType': 'ModeSwitchEvent',
                    'modeGroupInstanceRef': self.modeGroupInstance.id, 'activationType': self.activationType,
                    'modeInstanceName': self.modeInstance.name }
        return result


class TimingEventTrigger(Instance):
    def __init__(self, event, id = None):
        super().__init__(None, id)
        self.period = event.period

    def toDict(self):
        result = {'$id': self.id, 'triggerType': 'TimingEvent', 'period': self.period }
        return result

