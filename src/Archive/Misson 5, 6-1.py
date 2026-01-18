# Imports
import motor, time
from hub import port, sound

sleep = 0.35
sleep_before_going_back = 0.5

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
    motor.run(port.D, -speed)
    time.sleep(duration)
    motor.stop(port.D)


def move_extension_up(speed, duration):
    motor.run(port.D, speed)
    time.sleep(duration)
    motor.stop(port.D)

# Code for 1st Mission

move_forward(350, 4.62)

#time.sleep(sleep)

# Doing 1st Mission

turn_left(700, 0.23)

#time.sleep(sleep)

turn_right(500, 0.095)

# Code for 2nd Mission

#time.sleep(sleep)

move_forward(500, 0.2)

turn_left(100, 0.15)

#time.sleep(0.5)

# Doing 2nd Mission

turn_left(100, 0.7)

#time.sleep(sleep)

# Going Home

move_backward(500, 0.15)

#time.sleep(sleep)

turn_left(400, 0.37)

move_forward(1000, 1.2)

turn_left(300, 0.6)

move_forward(800, 0.65)
