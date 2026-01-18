# Imports
import motor, time
from hub import port, sound

def move_forward(speed, duration):
    # Move forward: left motor: -speed, right motor: speed
    motor.run(port.A, -speed)
    motor.run(port.E, speed)
    time.sleep(duration)
    motor.stop(port.A)
    motor.stop(port.E)

def move_backward(speed, duration):
    motor.run(port.A, speed)
    motor.run(port.E, -speed)
    time.sleep(duration)
    motor.stop(port.A)
    motor.stop(port.E)

def turn_left(speed, duration):
    # Turn in place 180Â° to the left:
    # left motor runs at positive speed (i.e. in reverse relative to forward)
    # right motor runs at positive speed (i.e. forward relative to forward)
    motor.run(port.A, speed)
    motor.run(port.E, speed)
    time.sleep(duration)# Adjust duration for an accurate 180Â° turn
    motor.stop(port.A)
    motor.stop(port.E)

def turn_right(speed, duration):
    # Turn in place 180Â° to the left:
    # left motor runs at positive speed (i.e. in reverse relative to forward)
    # right motor runs at positive speed (i.e. forward relative to forward)
    motor.run(port.A, -speed)
    motor.run(port.E, -speed)
    time.sleep(duration)# Adjust duration for an accurate 180Â° turn
    motor.stop(port.A)
    motor.stop(port.E)

def move_extension_down(speed, duration):
    motor.run(port.D, speed)
    time.sleep(duration)
    motor.stop(port.D)


def move_extension_up(speed, duration):
    motor.run(port.D, -speed)
    time.sleep(duration)
    motor.stop(port.D)

# Code for 1st Mission

move_forward(300, 5.25)

# Doing 1st Mission

turn_left(700, 0.23)

# Code for 2nd Mission

move_forward(500, 0.2)

turn_left(100, 0.15)

# Doing 2nd Mission

turn_left(100, 0.7)

move_backward(1000, 0.1)

# Turning towards Milestone

turn_left(200, 2.8)

# Moves Extension to yeet Millstone

move_extension_down(90, 1.71)

# Move Forward

move_forward(150, 0.18)

# Turn to Yeet Mission

turn_right(500, 0.25)

move_extension_down(90, 0.15)

time.sleep(0.2)

# Redundancy

turn_left(500, 0.23)

# Going Back

move_backward(150, 0.2)

move_extension_up(90, 1.72)

move_backward(150, 0.5)

# Turning Before Going Home

turn_left(300, 0.18)

move_backward(800, 1.3)

turn_left(300, 0.6)

move_backward(800, 1)
