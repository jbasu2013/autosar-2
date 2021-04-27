import cfile as C
import os
import io
from amber.rte.generator.common import genCommentHeader


class EventGenerator:
    def __init__(self, partition):
        self.partition = partition

    def genHeader(self, dest_dir = '.'):
        """
        Generates os_event_cfg.h
        """
        pass
