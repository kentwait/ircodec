"""
Classes used to represent infrared pulses and gaps.
"""
import json


class Signal(object):
    """Generic IR signal class.
    """
    def __init__(self, length):
        """Creates a new IR signal object.

        Parameters
        ----------
        length : int
            Length of the IR signal
        
        """
        self.length = length

    @classmethod
    def from_json(cls, data):
        if isinstance(data, str):
            dct = json.loads(json_string)
        elif isinstance(data, dict):
            dct = data
        return cls(dct['length'])

    def to_json(self):
        return json.dumps(self, default=lambda o: {**{'type': o.__class__.__name__}, **o.__dict__})

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.length)


class Pulse(Signal):
    """Represents an IR pulse.
    """
    def __init__(self, length):
        """Creates a new IR pulse object.

        Parameters
        ----------
        length : int
            Length of the IR pulse

        """
        super().__init__(length)


class Gap(Signal):
    """Represents a gap between IR pulses.
    """
    def __init__(self, length):
        """Creates a new gap object.

        Parameters
        ----------
        length : int
            Length of the gap between two IR pulses

        """
        super().__init__(length)


class SignalClass(object):
    """SignalClass is a set of signals with similar durations
    such that they are considered all to be the same signal.

    The duration variance may have been caused by variance at the source
    or imprecise measurement when the signals were received.
    """
    uid = 0
    unit = Signal
    def __init__(self, signal_list):
        """Creates a new signal class from a list of
        similar signals considered to be the same.

        Parameters
        ----------
        signal_list : list of Signal
            List of Signal objects

        """
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
    
    def normalized(self, normalized_value='int_mean'):
        if normalized_value == 'mean':
            return self.__class__.unit(self.mean)
        elif normalized_value == 'int_mean':
            return self.__class__.unit(int(self.mean))
        elif normalized_value == 'mode':
            return self.__class__.unit(self.mode)
        elif normalized_value == 'min':
            return self.__class__.unit(self.min)
        elif normalized_value == 'max':
            return self.__class__.unit(self.max)
        raise ValueError('Unrecognized normalized_value: {}'.format(normalized_value))

    @classmethod
    def from_json(cls, data):
        if isinstance(data, str):
            dct = json.loads(json_string)
        elif isinstance(data, dict):
            dct = data
        sig_cls = cls.__new__(cls)
        for name, value in dct.items():
            if name == 'type':
                continue
            sig_cls.__setattr__(name, value)
        if sig_cls.__class__.uid < sig_cls.uid:
            sig_cls.__class__.uid = sig_cls.uid
        return sig_cls

    def to_json(self):
        return json.dumps(self, default=lambda o: {**{'type': o.__class__.__name__}, **o.__dict__})

    def __contains__(self, signal):
        if signal.length >= self.min and signal.length <= self.max:
            return True
        return False

    def __repr__(self):
        return "{}(uid={})".format(self.__class__.__name__, self.uid)


class PulseClass(SignalClass):
    """PulseClass is a set of IR pulses with similar durations
    such that they are considered all to be the same IR pulse with some variance.
    """
    uid = 0
    unit = Pulse
    def __init__(self, signal_list):
        """Creates a new pulse class from a list of
        similar IR pulses considered to be the same.

        Parameters
        ----------
        signal_list : list of Pulse
            List of Pulse objects

        """
        super().__init__(signal_list)
        self.id = self.__class__.uid
        self.__class__.uid += 1

    def __repr__(self):
        return "{}(uid={}, id={})".format(self.__class__.__name__, self.uid, self.id)


class GapClass(SignalClass):
    """GapClass is a set of gaps with similar durations
    such that they are considered all to be the same kind of gap with some variance.
    """
    uid = 0
    unit = Gap
    def __init__(self, signal_list):
        """Creates a new gap class from a list of
        similar gaps considered to be the same.

        Parameters
        ----------
        signal_list : list of Gap
            List of Gap objects

        """
        super().__init__(signal_list)
        self.id = self.__class__.uid
        self.__class__.uid += 1

    def __repr__(self):
        return "{}(uid={}, id={})".format(self.__class__.__name__, self.uid, self.id)


def group_signals(signal_list, tolerance=0.1):
    """Groups signals into signal classes using a given tolerance value.

    Parameters
    ----------
    signal_list : list of Signal
        List members are either all Pulse objects or all Gap objects
    
    Returns
    -------
    list of list of Signal
        Each sublist contains the sorted durations believed to be variants
        of a single type of signal.

    """
    sorted_signals = sorted(signal_list, key=lambda x: x.length)
    
    signal_grouping = [[]]
    group_id = 0
    max_tol = 1 + tolerance

    signal_grouping[group_id].append(sorted_signals[0])
    for a, b in zip(sorted_signals[:-1], sorted_signals[1:]):
        if b.length < a.length * max_tol:
            signal_grouping[group_id].append(b)
        else:
            signal_grouping.append([b])
            group_id += 1
    return signal_grouping
