# ircodec

A Python package that simplifies sending and receiving IR signals for the Raspberry Pi using pigpiod.

## Requirements
- [pigpio daemon](http://abyz.me.uk/rpi/pigpio/pigpiod.html)
- [pigpio Python package](http://abyz.me.uk/rpi/pigpio/python.html)  
```
pip install pigpio
```

## Install
For Raspbian 9 (stretch)
```
pip install ircodec
```

For others
```
git clone git@github.com:kentwait/ircodec.git
cd ircodec
python setup.py install
```

## Quickstart
```python
# Create a CommandSet for your remote control
# GPIO for the IR receiver: 23
# GPIO for the IR transmitter: 22
from ircodec.command import CommandSet
controller = CommandSet(name='TV', emitter_gpio=22, receiver_gpio=23, description='TV remote')

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

# Save to JSON
controller.save_as('tv.json')

# Load from JSON
new_controller = CommandSet.load('another_tv.json')

```

## Acknowledgment
[pigpio Python examples](http://abyz.me.uk/rpi/pigpio/examples.html#Python%20code)

## Contact
kentkawashima@gmail.com


License: MIT License  
