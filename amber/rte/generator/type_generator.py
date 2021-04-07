import cfile as C
import os
import io
from amber.rte.generator.common import genCommentHeader


class TypeGenerator:

    def __init__(self, partition):
        self.partition = partition

    def genTypeHeader(self, dest_dir = '.'):
        """
        Generates Rte_Type.h
        """

        file_name = 'Rte_Type.h'
        file_path = os.path.join(dest_dir, file_name)
        hfile=C.hfile(file_name)
        hfile.code.extend(genCommentHeader('Includes'))
        hfile.code.append(C.include("Rte.h"))
        hfile.code.append(C.blank())
        hfile.code.extend(genCommentHeader('Data Type Definitions'))
        hfile.code.append(C.blank())
        for dataType in self.partition.dataTypeTable.values():
            if not dataType.skipGeneration:
                self._declare_type(hfile.code, dataType)
        with io.open(file_path, 'w', newline='\n') as fp:
            fp.write('\n'.join(hfile.lines()))
            fp.write('\n')
        
    def _declare_type(self, code, dataType):
        if dataType.targetType is not None:
            code.append(C.statement(C.typedef(dataType.targetType.name, dataType.name)))
        




