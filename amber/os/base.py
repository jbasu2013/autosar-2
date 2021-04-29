import autosar.base

class Task:
    def __init__(self, name):
        self.name = name
        self.nextEventBit = 1
        self.eventList = []
        self.alarmList = []

    def createTimerEvent(self, offset, period):
        name = "Rte_Ev_Cyclic_{0.name}_{1:d}_{2:d}ms".format(self, offset, period)
        event = self.createEvent(name)
        self.createAlarm(event, offset, period)
        return event

    def createEvent(self, name):
        bitMask = self._createBitMask()
        event = Event(name, bitMask)
        self.eventList.append(event)
        return event

    def createAlarm(self, event, offset, period):
        alarm = Alarm(event, offset, period)
        self.alarmList.append(alarm)

    def _createBitMask(self):
        if (self.nextEventBit >= 32):
            raise RuntimeError('Event-limit reached in task: ' + self.name)
        retval = self.nextEventBit
        self.nextEventBit <<= 1
        return retval

class Event:
    def __init__(self, name, bitMask):
        self.name = name
        self.bitMask = bitMask

class Alarm:
    def __init__(self, event, offset, period):
        self.event = event
        self.offset = offset
        self.period = period
