# Imports
import motor, time
from hub import port, sound

def move_forward(speed, duration):
    # Move forward: left motor: -speed, right motor: speed
    motor.run(port.D, speed)
    motor.run(port.C, -speed)
    time.sleep(duration)
    motor.stop(port.D)
    motor.stop(port.C)

def move_backward(speed, duration):
    motor.run(port.D, -speed)
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.D)
    motor.stop(port.C)

def turn_left(speed, duration):
    # Turn in place 180Â° to the left:
    # left motor runs at positive speed (i.e. in reverse relative to forward)
    # right motor runs at positive speed (i.e. forward relative to forward)
    motor.run(port.D, -speed)
    motor.run(port.C, -speed)
    time.sleep(duration)# Adjust duration for an accurate 180Â° turn
    motor.stop(port.D)
    motor.stop(port.C)

def turn_right(speed, duration):
    # Turn in place 180Â° to the left:
    # left motor runs at positive speed (i.e. in reverse relative to forward)
    # right motor runs at positive speed (i.e. forward relative to forward)
    motor.run(port.D, speed)
    motor.run(port.C, speed)
    time.sleep(duration)# Adjust duration for an accurate 180Â° turn
    motor.stop(port.D)
    motor.stop(port.C)

def move_extension_up(speed, duration):
    motor.run(port.A, speed)
    time.sleep(duration)
    motor.stop(port.A)


def move_extension_down(speed, duration):
    motor.run(port.A, -speed)
    time.sleep(duration)
    motor.stop(port.A)

# Extension Calibration

move_extension_up(500, 0.5)

time.sleep(0.5)

move_extension_down(500, 0.15)

time.sleep(1.2)

# Movement Code for Mission 1

move_forward(300, 4)

turn_right(500, 1)

turn_left(500, 1.2)
