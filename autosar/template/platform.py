import autosar
class AUTOSAR_Platform(autosar.Template):
    """AUTOSAR Platform Package"""
    static_ref = '/AUTOSAR_Platform'

    @classmethod
    def apply(cls, ws):
        package = ws.find(cls.ref(ws))
        if package is None:
            package = ws.createPackage('AUTOSAR_Platform')
            baseTypes = package.createSubPackage('BaseTypes', role='DataType')
            package.createSubPackage('CompuMethods', role='CompuMethod')
            package.createSubPackage('DataConstrs', role='DataConstraint')
            implTypes = package.createSubPackage('ImplementationDataTypes')
            baseTypes.createSwBaseType('dtRef_const_VOID', 1, encoding = 'VOID', nativeDeclaration = 'void')
            baseTypes.createSwBaseType('dtRef_VOID', 1, encoding = 'VOID', nativeDeclaration = 'void')
            baseTypes.createSwBaseType('boolean', 8, encoding = 'BOOLEAN', nativeDeclaration='boolean')
            baseTypes.createSwBaseType('float32', 32, encoding = 'IEEE754', nativeDeclaration = 'float32')
            baseTypes.createSwBaseType('float64', 64, encoding = 'IEEE754', nativeDeclaration = 'float64')
            baseTypes.createSwBaseType('sint8', 8, encoding = '2C', nativeDeclaration='sint8')
            baseTypes.createSwBaseType('sint16', 16, encoding = '2C', nativeDeclaration='uint16')
            baseTypes.createSwBaseType('sint32', 32, encoding = '2C', nativeDeclaration='sint32')
            baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
            baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
            baseTypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
            ws.pushRoles()
            ws.setRole(implTypes.ref, 'DataType')
            implTypes.createImplementationDataTypePtr('dtRef_const_VOID', '/AUTOSAR_Platform/BaseTypes/dtRef_const_VOID', swImplPolicy = 'CONST')
            implTypes.createImplementationDataTypePtr('dtRef_VOID', '/AUTOSAR_Platform/BaseTypes/dtRef_VOID')
            implTypes.createImplementationDataType('boolean', '/AUTOSAR_Platform/BaseTypes/boolean', valueTable=['FALSE', 'TRUE'], typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('uint8', '/AUTOSAR_Platform/BaseTypes/uint8', lowerLimit=0, upperLimit=255, typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('uint16', '/AUTOSAR_Platform/BaseTypes/uint16', lowerLimit=0, upperLimit=65535, typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('uint32', '/AUTOSAR_Platform/BaseTypes/uint32', lowerLimit=0, upperLimit=4294967295, typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('sint8', '/AUTOSAR_Platform/BaseTypes/sint8', lowerLimit=-128, upperLimit=127, typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('sint16', '/AUTOSAR_Platform/BaseTypes/sint16', lowerLimit=-32768, upperLimit=32767, typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('sint32', '/AUTOSAR_Platform/BaseTypes/sint32', lowerLimit=-2147483648, upperLimit=2147483647, typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('float32', '/AUTOSAR_Platform/BaseTypes/float32',
                lowerLimit='-INF', upperLimit='INF', lowerLimitType='OPEN', upperLimitType='OPEN',
                typeEmitter='Platform_Type')
            implTypes.createImplementationDataType('float64', '/AUTOSAR_Platform/BaseTypes/float64',
                lowerLimit='-INF', upperLimit='INF', lowerLimitType='OPEN', upperLimitType='OPEN',
                typeEmitter='Platform_Type')
            ws.popRoles()
    
    class BaseTypes:

        class uint8(autosar.Template):

            @classmethod
            def ref(cls, ws): return '/AUTOSAR_Platform/BaseTypes/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)

        class uint16(autosar.Template):

            @classmethod
            def ref(cls, ws): return '/AUTOSAR_Platform/BaseTypes/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)

        class uint32(autosar.Template):

            @classmethod
            def ref(cls, ws): return '/AUTOSAR_Platform/BaseTypes/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)                

    class ImplementationDataTypes:

        class uint8(autosar.Template):

            @classmethod
            def ref(cls, ws): return '/AUTOSAR_Platform/ImplementationDataTypes/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)

        class uint16(autosar.Template):

            @classmethod
            def ref(cls, ws): return '/AUTOSAR_Platform/ImplementationDataTypes/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)

        class uint32(autosar.Template):

            @classmethod
            def ref(cls, ws): return '/AUTOSAR_Platform/ImplementationDataTypes/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)


