"""
Classes used to represent infrared pulses and gaps.
"""

class Signal:
    def __init__(self, length):
        self.length = length

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.length)


class Pulse(Signal):
    pass


class Gap(Signal):
    pass


class SignalClass:
    uid = 0
    def __init__(self, signal_list):
        self.uid = self.__class__.uid
        self.__class__.uid += 1

        self.signals = [x.length for x in signal_list]
        self.mean = sum(self.signals) / len(self.signals)
        self.mode = max(set(self.signals), key=self.signals.count)
        self.min = min(self.signals)
        self.max = max(self.signals)
        self.range = self.max - self.min

    @property
    def minmax(self):
        return self.min, self.max

    @property
    def count(self):
        return len(self.signals)

    def istype(self, signal):
        if signal.length >= self.min and signal.length <= self.max:
            return True
        return False

    def __repr__(self):
        return "{}(uid={})".format(self.__class__.__name__, self.uid)


class PulseClass(SignalClass):
    id = 0
    def __init__(self, signal_list):
        super().__init__(signal_list)
        self.id = self.__class__.id
        self.__class__.id += 1

    def __repr__(self):
        return "{}(uid={}, id={})".format(self.__class__.__name__, self.uid, self.id)


class GapClass(SignalClass):
    id = 0
    def __init__(self, signal_list):
        super().__init__(signal_list)
        self.id = self.__class__.id
        self.__class__.id += 1

    def __repr__(self):
        return "{}(uid={}, id={})".format(self.__class__.__name__, self.uid, self.id)
