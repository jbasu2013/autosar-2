import cfile as C
import os
import io

def beginExternCBlock():
    code = C.sequence()
    code.append(C.line('#ifdef __cplusplus'))
    code.append(C.line('extern "C"'))
    code.append(C.line('{'))
    code.append(C.line('#endif /* __cplusplus */'))
    return code

def endExternCBlock():
    code = C.sequence()
    code.append(C.line('#ifdef __cplusplus'))
    code.append(C.line('}'))
    code.append(C.line('#endif /* __cplusplus */'))
    return code

def genCommentHeader(comment):
    """
    Returns a comment header
    """
    code = C.sequence()
    code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
    code.append(C.line('// {}'.format(comment)))
    code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
    return code

class TaskGenConfig:
    def __init__(self, name):
        self.name = name
        self.vars = {}
        self.alarms = []

class EventGenerator:
    def __init__(self, partition):
        self.partition = partition

    def genHeader(self, dest_dir = '.'):
        """
        Generates os_event_cfg.h
        """
        file_name = 'os_event_cfg.h'
        file_path = os.path.join(dest_dir, file_name)
        hfile=C.hfile(file_name)
        hfile.code.extend(genCommentHeader('INCLUDES'))
        hfile.code.append(C.include("amber/os_types.h"))
        hfile.code.append(C.blank())
        hfile.code.extend(genCommentHeader('PUBLIC CONSTANTS AND DATA TYPES'))
        hfile.code.append(C.blank())
        for task in self.partition.taskTable.values():
            for event in task.eventList:
                text = "((os_eventMask_t) 0x{:08x}u)".format(event.bitMask)
                hfile.code.append(C.define(event.name, text))
        with io.open(file_path, 'w', newline='\n') as fp:
            fp.write('\n'.join(hfile.lines()))
            fp.write('\n')

class TaskGenerator:
    def __init__(self, partition):
        self.partition = partition
        self.vars = {}
        self.vars['os_task_cfg'] = C.variable('os_task_cfg', 'os_taskCfg_t', const = 1, extern = 1, array='OS_NUM_TASKS')
        self.vars['os_task_instance'] = C.variable('os_task_instance', 'os_task_t', pointer = 1, extern = 1, array='OS_NUM_TASKS')
        self.tasks = []
        for task in partition.taskTable.values():
            taskGenCfg = TaskGenConfig(task.name)
            if len(task.alarmList) > 0:
                taskGenCfg.vars['os_alarm_cfg'] = C.variable('os_alarm_cfg_'+task.name, 'os_alarmCfg_t', static=1, const=1, array='OS_NUM_ALARMS_'+task.name)
                for alarm in task.alarmList:
                    taskGenCfg.alarms.append((str(alarm.event.name), int(alarm.offset), int(alarm.period)))
            self.tasks.append(taskGenCfg)

        #static const os_alarmCfg_t os_alarm_cfg_Rte_Task[OS_NUM_ALARMS_Rte_Task]

    def genHeader(self, dest_dir = '.'):
        """
        Generates os_task_cfg.h
        """
        file_name = 'os_task_cfg.h'
        file_path = os.path.join(dest_dir, file_name)
        hfile=C.hfile(file_name)
        hfile.code.extend(genCommentHeader('INCLUDES'))
        hfile.code.append(C.include("amber/os_types.h"))
        hfile.code.append(C.include("amber/os_task.h"))
        hfile.code.append(C.blank())
        hfile.code.extend(genCommentHeader('PUBLIC CONSTANTS AND DATA TYPES'))
        hfile.code.append(C.blank())
        for task in self.partition.taskTable.values():
            numAlarms = len(task.alarmList)
            numEvents = len(task.eventList)
            hfile.code.append(C.define("OS_NUM_ALARMS_"+task.name, numAlarms))
            hfile.code.append(C.define("OS_NUM_EVENTS_"+task.name, numEvents))
        hfile.code.append(C.blank())
        hfile.code.extend(genCommentHeader('PUBLIC VARIABLES'))
        hfile.code.append(C.blank())
        hfile.code.append(C.statement(self.vars['os_task_cfg']))
        hfile.code.append(C.statement(self.vars['os_task_instance']))
        hfile.code.append(C.blank())
        hfile.code.extend(genCommentHeader('PUBLIC FUNCTION PROTOTYPES'))
        hfile.code.append(C.statement('OS_TASK_HANDLER(Rte_Task, arg)'))
        with io.open(file_path, 'w', newline='\n') as fp:
            fp.write('\n'.join(hfile.lines()))
            fp.write('\n')

    def genSource(self, dest_dir = '.'):
        """
        Generates os_task_cfg.c
        """
        file_name = 'os_task_cfg.c'
        file_path = os.path.join(dest_dir, file_name)
        cfile=C.cfile(file_name)
        cfile.code.extend(genCommentHeader('INCLUDES'))
        cfile.code.append(C.include("os_event_cfg"))
        cfile.code.append(C.include("os_task_cfg.h"))
        cfile.code.append(C.blank())
        cfile.code.extend(genCommentHeader('PRIVATE VARIABLES'))
        cfile.code.append(C.blank())
        for taskGenCfg in self.tasks:
            if 'os_alarm_cfg' in taskGenCfg.vars:
                cfile.code.append(C.line("{} = ".format(str(taskGenCfg.vars['os_alarm_cfg']))))
                block = C.block(innerIndent=3)
                block.append(C.linecomment('Event, Init Delay (ms), Period (ms)'))
                for initValues in taskGenCfg.alarms:
                    block.append(C.line('{{{0}, {1:d}u, {2:d}u}},'.format(*initValues)))
                cfile.code.append(C.statement(block))
        cfile.code.append(C.blank())
        cfile.code.extend(genCommentHeader('PUBLIC VARIABLES'))
        cfile.code.append(C.blank())
        self.vars['os_task_cfg'].extern=0
        cfile.code.append(C.line("{} = ".format(str(self.vars['os_task_cfg']))))
        self.vars['os_task_cfg'].extern=1
        block = C.block(innerIndent=3)
        for taskGenCfg in self.tasks:
            if 'os_alarm_cfg' in taskGenCfg.vars:
                block.append(C.line('{{{0.name}, &os_alarm_cfg_{0.name}[0], OS_NUM_ALARMS_{0.name}}},'.format(taskGenCfg)))
            else:
                block.append(C.line('{{{0.name}, NULL, 0u}},'))

        cfile.code.append(C.statement(block))
        self.vars['os_task_instance'].extern=0
        cfile.code.append(C.line("{} = ".format(str(self.vars['os_task_instance']))))
        self.vars['os_task_instance'].extern=1
        block = C.block(innerIndent=3)
        for taskGenCfg in self.tasks:
            block.append(C.line('NULL,'))
        cfile.code.append(C.statement(block))
        with io.open(file_path, 'w', newline='\n') as fp:
            fp.write('\n'.join(cfile.lines()))
            fp.write('\n')

