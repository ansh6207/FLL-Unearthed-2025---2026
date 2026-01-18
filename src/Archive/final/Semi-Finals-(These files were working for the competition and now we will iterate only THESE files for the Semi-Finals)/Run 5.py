import motor, time
from hub import port, sound

sleep = 0.3

def move_forward(speed, duration):
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

def turn_right(speed, duration):
    motor.run(port.A, -speed)
    time.sleep(duration)
    motor.stop(port.A)

def turn_left(speed, duration):
    motor.run(port.E, speed)
    time.sleep(duration)
    motor.stop(port.E)

def backwards_left(speed, duration):
    motor.run(port.E, -speed)

    time.sleep(duration)
    motor.stop(port.E)

def backwards_right(speed, duration):
    motor.run(port.A, speed)
    time.sleep(duration)
    motor.stop(port.A)

def right_attachment(speed, duration):
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.C)

def left_attachment(speed, duration):
    motor.run(port.C, -speed)
    time.sleep(duration)
    motor.stop(port.C)

def move_extension_down(speed, duration):
    motor.run(port.D, speed)
    time.sleep(duration)
    motor.stop(port.D)


def move_extension_up(speed, duration):
    motor.run(port.D, -speed)
    time.sleep(duration)
    motor.stop(port.D)

# Right = Up
# Left = Down

# Do First Part of Mission 1

move_backward(510, 1.5)

# Do Second Part of Mission 1

move_forward(600, 0.8)

move_backward(600, 0.6)

# Turn Toward Mission 2

backwards_left(455, 1.5)

# Move Extension Down Before Doing 1st Part Of Mission 2

left_attachment(200, 0.67)

# Do 1st Part Of Mission 2

move_forward(500, 0.8)

# Move Extension Up a Bit

right_attachment(370, 0.1)

# Get Out of There

move_backward(410, 0.4)

# Do 2nd Part Of Mission 2

turn_right(600, 2)

right_attachment(200, 0.67)

# Come Home

move_forward(1000, 1.6)
