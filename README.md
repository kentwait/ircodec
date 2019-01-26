# ircodec

A Python package that simplifies sending and receiving IR signals for the Raspberry Pi using pigpiod.

## Requirements
- [pigpio daemon](http://abyz.me.uk/rpi/pigpio/pigpiod.html)
- [pigpio Python package](http://abyz.me.uk/rpi/pigpio/python.html)  
```
pip install pigpio
```

## Install
```
pip install ircodec
```

## Quickstart
```python
# Create a CommandSet for your remote control
# GPIO for the IR receiver: 23
# GPIO for the IR transmitter: 22
from ircodec.command import CommandSet
controller = CommandSet(emitter_gpio=22, receiver_gpio=23, description='TV remote')

# Add the volume up key
controller.add('volume_up')
# Connected to pigpio
# Detecting IR command...
# Received.

# Send the volume up command
controller.emit('volume_up')

# Remove the volume up command
controller.remove('volume_up')

# Examine the contents of the CommandSet
controller
# CommandSet(emitter=22, receiver=23, description="TV remote")
# {}
```

License: MIT License  
Contact: kentkawashima@gmail.com
