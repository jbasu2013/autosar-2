import autosar.base

class Task:
    def __init__(self, name):
        self.name = name
        self.nextEventBit = 1
        self.events = {}
        self.alarms = {}

    def createTimerEvent(self, offset, period):
        name = "Rte_Ev_Cyclic_{0.name}_{1:d}_{2:d}ms".format(self, offset, period)
        bitMask = self._createBitMask()
        event = TimerEvent(name, bitMask, int(period))
        self.events[name] = event
        return event

    def createEvent(self, name):
        bitMask = self._createBitMask()
        event = Event(name, bitMask)
        self.events[name] = event
        return event


    def _createBitMask(self):
        if (self.nextEventBit >= 32):
            raise RuntimeError('Event-limit reached in task: ' + self.name)
        retval = self.nextEventBit
        self.nextEventBit = self.nextEventBit**2
        return retval

class Event:
    def __init__(self, name, bitMask):
        self.name = name
        self.bitMask = bitMask

class TimerEvent(Event):
    def __init__(self, name, bitMask, period):
        super().__init__(name, bitMask)
        self.period = period
