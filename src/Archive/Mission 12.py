import motor, time
from hub import port

sleep = 0.75

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
    motor.run(port.C, -speed)
    time.sleep(duration)
    motor.stop(port.C)


def move_extension_up(speed, duration):
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.C)

#Mission Code

move_forward(600, 1.2)

move_extension_down(300, 0.5)

turn_right(300, 0.155)

move_backward(500, 0.4)

move_forward(300, 0.25)

turn_left(300, 0.55)

move_extension_up(300, 0.35)

move_forward(300, 1.1)

turn_right(300, 0.3)

move_forward(300, 2)

# Coming Home

move_backward(1000, 1)

turn_left(300, 1.2)

move_forward(300, 2.3)

move_extension_down(300, 0.32)

turn_left(300, 0.7)

turn_right(300, 0.7)  r

move_extension_down(300, 0.2)

move_forward(300, 1.0)

#move_backward(1000, 0.75)
