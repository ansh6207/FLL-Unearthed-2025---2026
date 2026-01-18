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
    motor.run(port.D, -speed)
    time.sleep(duration)
    motor.stop(port.D)


def move_extension_up(speed, duration):
    motor.run(port.D, speed)
    time.sleep(duration)
    motor.stop(port.D)

def move_extension_left(speed, duration): # left = up
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.C)


def move_extension_right(speed, duration): # right = down
    motor.run(port.C, -speed)
    time.sleep(duration)
    motor.stop(port.C)

def Silo():
    move_extension_right(750, 0.2)
    time.sleep(0.3)
    move_extension_left(300, 0.2)
    time.sleep(0.4)

move_forward(300, 0.9)

Silo()
Silo()
Silo()

move_backward(1000, 0.55)

turn_left(300, 0.5)

move_forward(450, 1.5)

move_extension_right(300, 0.2)

turn_left(300, 0.6)

move_extension_left(300, 0.2)

turn_right(300, 0.3)

move_backward(1000, 0.9)
