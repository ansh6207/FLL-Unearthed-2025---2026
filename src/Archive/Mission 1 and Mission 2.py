# Imports
import motor, time
from hub import port, sound

def move_forward(speed, duration):
    # Move forward: left motor: -speed, right motor: speed
    motor.run(port.A, speed)
    motor.run(port.E, -speed)
    time.sleep(duration)
    motor.stop(port.A)
    motor.stop(port.E)

def move_backward(speed, duration):
    motor.run(port.A, -speed)
    motor.run(port.E, speed)
    time.sleep(duration)
    motor.stop(port.A)
    motor.stop(port.E)

def turn_left(speed, duration):
    # Turn in place 180Â° to the left:
    # left motor runs at positive speed (i.e. in reverse relative to forward)
    # right motor runs at positive speed (i.e. forward relative to forward)
    motor.run(port.A, -speed)
    motor.run(port.E, -speed)
    time.sleep(duration)# Adjust duration for an accurate 180Â° turn
    motor.stop(port.A)
    motor.stop(port.E)

def turn_right(speed, duration):
    # Turn in place 180Â° to the left:
    # left motor runs at positive speed (i.e. in reverse relative to forward)
    # right motor runs at positive speed (i.e. forward relative to forward)
    motor.run(port.A, speed)
    motor.run(port.E, speed)
    time.sleep(duration)# Adjust duration for an accurate 180Â° turn
    motor.stop(port.A)
    motor.stop(port.E)

def move_extension_up(speed, duration):
    motor.run(port.D, speed)
    time.sleep(duration)
    motor.stop(port.D)


def move_extension_down(speed, duration):
    motor.run(port.D, -speed)
    time.sleep(duration)
    motor.stop(port.D)

# Extension Calibration

move_extension_down(500, 0.515)

time.sleep(1.5)

move_extension_up(500, 0.188511)

time.sleep(1.2)

# Movement Code for Mission 1

move_forward(300, 2.5)

turn_right(300, 1)

turn_left(300, 1)

# Movement code for Mission 2 (Part 1)

move_extension_down(500, 0.05)

time.sleep(0.5)

move_forward(300, 0.5)

time.sleep(0.5)

turn_right(300, 0.193635)

time.sleep(0.5)

move_forward(500, 0.2)

time.sleep(0.5)

move_extension_up(500, 0.5)

time.sleep(0.5)

turn_left(300, 0.15)

time.sleep(0.5)

move_backward(500, 3)

print("Code Compiled Succsess!")

# Movement code for Mission 2 (Part 2)
