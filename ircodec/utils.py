import pigpio

def carrier_square_wave_generator(gpio, frequency, signal_length):
    """
    Generate carrier square wave.
    """
    waveform = []
    # frequency is number of cycles per second, usually 38 kHz
    micro_per_cycle = 1000.0 / frequency  # 1 / kHz is millisecond, * 1000 is microsecond
    # number of cycles during the signal
    # signal_length is in microseconds
    num_cycles = int(round(signal_length / micro_per_cycle))

    on = int(round(micro_per_cycle / 2.0))  # signal length is in microseconds
    sofar = 0

    # from zero cycles to target cycles
    for c in range(num_cycles):
        target = int(round((c+1) * micro_per_cycle))  # target is time in ms
        sofar += on
        off = target - sofar
        sofar += off

        # pigpio.pulse(gpio_on, gpio_off, delay)
        # gpio_on  - the GPIO to switch on at the start of the pulse.
        # gpio_off - the GPIO to switch off at the start of the pulse.
        # delay    - the delay in microseconds before the next pulse.
        waveform.append(pigpio.pulse(1<<gpio, 0, on))  # bitwise shift?
        waveform.append(pigpio.pulse(0, 1<<gpio, off))

    return waveform
