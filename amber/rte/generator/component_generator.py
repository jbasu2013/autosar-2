import cfile as C
import os
import io
from amber.rte.generator.common import *

class ComponentGenerator:
    def __init__(self, partition):
        self.partition = partition

    def genHeaders(self, destDir = '.'):
        """
        Generates RTE Component headers
        """
        for componentInstance in self.partition.componentTable.values():
            self._generateRteComponentHeader(componentInstance, destDir)
            self._generateRteComponentTypeHeader(componentInstance, destDir)

    def _generateRteComponentHeader(self, componentInstance, destDir):
        fileName = 'Rte_{0.name}.h'.format(componentInstance)
        filePath = os.path.join(destDir, fileName)
        hfile=C.hfile(fileName)
        hfile.code.extend(beginExternCBlock())
        hfile.code.extend(genCommentHeader('Includes'))
        hfile.code.append(C.include("Rte_{0.name}_Type.h".format(componentInstance)))
        hfile.code.append(C.blank())
        hfile.code.extend(genCommentHeader('Runnables'))
        for name in sorted(componentInstance.runnableTable.keys()):
            runnableInstance = componentInstance.runnableTable[name]
            hfile.code.append(C.statement(runnableInstance.functionPrototype))
        hfile.code.append(C.blank())
        hfile.code.extend(endExternCBlock())
        with io.open(filePath, 'w', newline='\n') as fp:
            fp.write('\n'.join(hfile.lines()))
            fp.write('\n')

    def _generateRteComponentTypeHeader(self, componentInstance, destDir):
        fileName = 'Rte_{0.name}_Type.h'.format(componentInstance)
        filePath = os.path.join(destDir, fileName)
        hfile=C.hfile(fileName)
        hfile.code.extend(beginExternCBlock())
        hfile.code.extend(genCommentHeader('Includes'))
        hfile.code.append(C.include("Rte_Type.h"))
        hfile.code.append(C.blank())
        hfile.code.extend(endExternCBlock())
        with io.open(filePath, 'w', newline='\n') as fp:
            fp.write('\n'.join(hfile.lines()))
            fp.write('\n')

