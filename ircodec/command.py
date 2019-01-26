"""
IR command class and functions
"""
import time
import pigpio
from ircodec.signal import Signal, PulseClass, GapClass
from ircodec.signal import group_signals
from ircodec.utils import carrier_square_wave_generator

class Command(object):
    """Represents an IR command
    """
    def __init__(self, ir_signal_list, description=''):
        self.signal_list = ir_signal_list
        self.description = description
        self.signal_class_list = None

    def normalize(self, tolerance=0.1):
        """Classifies signals based on a tolerance and normalizes
        the list of signals.

        Parameters
        ----------
        tolerance : float

        """
        pulse_classes, gap_classes = parse_command(self.signal_list, tolerance=tolerance)
        self.normalize_from_classes(pulse_classes, gap_classes)

    def normalize_with(self, pulse_classes, gap_classes):
        """Normalizes the list of IR pulses and gaps using a set of
        reference pulse classes and gap classes.

        Parameters
        ----------
        pulse_classes : list of PulseClass
        gap_classes : list of GapClass

        """
        self.signal_list, self.signal_class_list = \
            normalize_command(self.signal_list, pulse_classes, gap_classes, return_class=True)

    def emit(self, pi: pigpio.pi, emitter_gpio: int, freq=38.0, emit_gap=0.1):
        """Emits the IR command pulses and gaps to a connected
        Raspberry Pi using the pigpio daemon.

        Parameters
        ----------
        pi : pigpio.pi
            pigpio object that grants access to the Raspberry Pi GPIO.
        emmitter_gpio : int
            GPIO pin to output to
        freq : float
            Frequency in kHz
        emit_gap : float
            Gap in seconds

        """
        # Create wave
        pi.set_mode(emitter_gpio, pigpio.OUTPUT)
        pi.wave_add_new()
        signals = {}
        gaps = {}
        wave_list = [0] * len(self.signal_list)
        emit_time = time.time()
        for i, siglen in enumerate(self.signal_list):
            if i & 1: # Space
                if siglen not in gaps:
                    pi.wave_add_generic([pigpio.pulse(0, 0, siglen)])
                    gaps[siglen] = pi.wave_create()
                wave_list[i] = gaps[siglen]
            else: # Mark
                if siglen not in signals:
                    wf = carrier_square_wave_generator(emitter_gpio, freq, siglen)
                    pi.wave_add_generic(wf)
                    signals[siglen] = pi.wave_create()
                wave_list[i] = signals[siglen]
        delay = emit_time - time.time()
        if delay > 0.0:
            sleep(delay)
        # Create wave chain
        pi.wave_chain(wave_list)
        while pi.wave_tx_busy():
            sleep(0.002)
        emit_time = time.time() + emit_gap

        # Remove signal waves
        for signal in signals.values():
            pi.wave_delete(signal)
        # signals = {}

        # Remove gap values
        for gap in gaps.values():
            pi.wave_delete(gap)
        # gaps = {}
    
    @classmethod
    def receive(cls, pi: pigpio.pi, receiver_gpio: int, 
                description='', glitch=0.00000100, 
                pre_duration=0.2, post_duration=0.015, length_threshold=10):
        """Receives IR command pulses and gaps from GPIO pin of a connected
        Raspberry Pi using the pigpio daemon.

        Parameters
        ----------
        pi : pigpio.pi
            pigpio object that grants access to the Raspberry Pi GPIO.
        receiver_gpio : int
            GPIO pin to read signals from
        description : str
            Short description for the IR command
        glitch : float
            Ignore edges shorter than this duration (seconds)
        pre_duration : float
            Expected number of seconds of silence before start of IR signals
        post_duration : float
            Expected number of seconds of silence after completion of IR signals
        length_threshold : float
            Reject detected IR command if it has less than this number of pulses

        """
        # Convert values seconds to microsends
        glitch = glitch * 1000 * 1000
        pre_duration = pre_duration * 1000 * 1000
        post_duration = post_duration * 1000 * 1000

        # Set initial values
        fetching_code = True
        ir_signal_list = []
        in_code = False
        last_tick = 0

        # Define callback function
        def callback(gpio, level, tick):
            nonlocal fetching_code, ir_signal_list, in_code, last_tick
            if level != pigpio.TIMEOUT:
                edge = pigpio.tickDiff(last_tick, tick)
                last_tick = tick

                if fetching_code == True:
                    if (edge > pre_duration) and (not in_code): # Start of a code.
                        in_code = True
                        pi.set_watchdog(receiver_gpio, post_duration) # Start watchdog.
                    elif (edge > post_duration) and in_code: # End of a code.
                        in_code = False
                        pi.set_watchdog(receiver_gpio, 0) # Cancel watchdog.
                        # Finish
                        if len(ir_signal_list) > length_threshold:
                            fetching_code = False
                        else:
                            ir_signal_list = []
                            raise ValueError("Received IR command is too short, please try again")
                    elif in_code:
                        ir_signal_list.append(edge)
            else:
                pi.set_watchdog(receiver_gpio, 0) # Cancel watchdog.
                if in_code:
                    in_code = False
                    # Finish
                    if len(ir_signal_list) > length_threshold:
                        fetching_code = False
                    else:
                        ir_signal_list = []
                        raise ValueError("Received IR command is too short, please try again")
        
        pi.set_mode(receiver_gpio, pigpio.INPUT) # IR RX connected to this GPIO.
        pi.set_glitch_filter(receiver_gpio, glitch) # Ignore glitches.
        # Assign a callback function
        cb = pi.callback(receiver_gpio, pigpio.EITHER_EDGE, callback)

        print("Receiving IR command...", end=' ')
        while fetching_code == True:
            time.sleep(0.1)
        print("Received.")

        pi.set_glitch_filter(receiver_gpio, 0) # Cancel glitch filter.
        pi.set_watchdog(receiver_gpio, 0) # Cancel watchdog.
    
    return cls(ir_signal_list, description=description)


def parse_command(ir_signal_list, tolerance=0.1):
    """Parses the set of IR pulses and gaps received from
    a single command into pulse and gap classes using a
    given tolerance value.

    Parameters
    ----------
    ir_signal_list : list of Signal
        List of pulses and gaps read by the IR receiver for a
        single command.
    tolerance : float
        Relative difference in duration of a signal compared to
        the next longer signal when pulses or gaps are arranged
        in increasing order. If the next signal falls outside the
        tolerance value, the next signal becomes the lower bound for
        a new signal class.
    
    Returns
    -------
    list of PulseClass, list of GapClass

    """
    # Separate interleaved pulses and gaps
    grouped_pulses = group_signals(ir_signal_list[::2])
    grouped_gaps = group_signals(ir_signal_list[1::2])

    # Classify into types
    pulse_classes = [PulseClass(pulses) for pulses in grouped_pulses.values()]
    gap_classes = [GapClass(gaps) for gaps in grouped_gaps.values()]

    return pulse_classes, gap_classes


def normalize_command(ir_signal_list, pulse_classes, gap_classes, return_class=False):
    """Creates a normalized series of IR pulses and gaps 
    for a particular IR command.

    Parameters
    ----------
    ir_signal_list : list of Signal
        List of pulses and gaps read by the IR receiver for a
        single command.
    pulse_classes : list of PulseClass
        PulseClass objects to compare to to create a normalized command
        from an unormalized signal list.
    gap_classes : list of GapClass
        GapClass objects to compare to to create a normalized command
        from an unormalized signal list.

    Returns
    -------
    list of Signal

    """
    signal_class_list = []
    for pulse, gap in zip(signal_list[:-1:2], signal_list[1::2]):
        pulse_type, gap_type = None, None
        for ptype in pulse_classes:
            if ptype.istype(pulse):
                pulse_type = ptype
        for gtype in gap_classes:
            if gtype.istype(gap):
                gap_type = gtype
        if pulse_type == None:
            raise Exception('Could not normalize pulse: {}'.format(pulse))
        if gap_type == None:
            raise Exception('Could not normalize gap: {}'.format(gap))
        signal_class_list.append(pulse_type)
        signal_class_list.append(gap_type)
    
    # Last pulse
    pulse = signal_list[-1]
    for ptype in pulse_classes:
        if ptype.istype(pulse):
            pulse_type = ptype
    if pulse_type == None:
        raise Exception('Could not normalize pulse: {}'.format(pulse))
    signal_class_list.append(pulse_type)

    normalized_signal_list =  [s.normalized() for s in signal_class_list]
    if return_class:
        return normalized_signal_list, signal_class_list
    return normalized_signal_list
