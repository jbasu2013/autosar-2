import autosar

class Amber(autosar.Template):
    static_ref = '/Amber'

    @classmethod
    def apply(cls, ws):
        if ws.find('Amber') is None:	
            package = ws.createPackage('Amber')
            package.createSubPackage('ComponentTypes')
            package.createSubPackage('ModeDeclarations')
            package.createSubPackage('PortInterfaces')
            dataTypes = package.createSubPackage('DataTypes')
            dataTypes.createSubPackage('CompuMethods')
            dataTypes.createSubPackage('DataConstraints')