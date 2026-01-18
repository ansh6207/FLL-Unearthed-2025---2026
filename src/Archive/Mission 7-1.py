sleep = 0.35

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

def move_extension_left(speed, duration): # left = up
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.C)


def move_extension_right(speed, duration): # right = down
    motor.run(port.C, -speed)
    time.sleep(duration)
    motor.stop(port.C)

# Main Program

move_forward(400, 3.95)#goes to the millstone

turn_right(150, 0.65)#turns to face the millstone

move_extension_down(100, 1.54)#moves extension to pick up millstone

move_forward(150, 0.9)#the arm goes into millstone

move_extension_up(100, 1.4)#millstone is picked up

move_backward(150, 0.9)#go backwards

turn_left(350, 0.65)#prepare to go toward forum

move_forward(400, 1.7)#Go to forum

turn_left(160, 0.45)#keep going

move_forward(400, 2.0)#still go

turn_left(160, 0.65)#turn towards forum

move_forward(100, 1.64)#almost dropping it...

move_extension_down(100, 1.44)#Dropped it!

move_backward(150, 0.9)#leave it there

move_extension_down(200, 0.5)#prepare for mineshaft

turn_right(410, 0.3) #Face toward mineshaft

time.sleep(1)

move_extension_up(150, 3.5)#lift it up

turn_left(400, 0.55)

move_forward(400, 2.2)

turn_right(400,0.42)

move_forward(1000, 3)
