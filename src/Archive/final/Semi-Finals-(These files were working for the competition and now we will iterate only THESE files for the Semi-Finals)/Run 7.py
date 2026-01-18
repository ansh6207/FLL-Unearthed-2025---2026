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

move_forward(400, 2)

turn_right(625, 0.5)

move_forward(400, 0.8)

left_attachment(200, 0.67)

move_forward(420, 0.4)

right_attachment(300, 0.5)
