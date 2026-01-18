#Step 1: Imports
import motor, time
from hub import port, sound

#Step 2: Make functions
#Forward function
def move_forward(speed, duration):
    #Starts motors
    motor.run(port.A, -speed)
    motor.run(port.E, speed)

    #Waits for duration time
    time.sleep(duration)

    #Stops motors
    motor.stop(port.A)
    motor.stop(port.E)

#Backward function
def move_backward(speed, duration):
    #Starts motors
    motor.run(port.A, speed)
    motor.run(port.E, -speed)

    #Waits for duration time
    time.sleep(duration)

    #Stops motors
    motor.stop(port.A)
    motor.stop(port.E)

#Turning functions
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

#Attatchment functions
def right_attachment(speed, duration):
    motor.run(port.D, speed)
    time.sleep(duration)
    motor.stop(port.D)

def left_attachment(speed, duration):
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.C)

#Step 3: Code
move_backward(700, 2) #Exit launch area + activate brush
move_forward(500, 1) #Activate brush other way
move_backward(500, 0.5) #Activate once more just in case
move_forward(500, 0.35) #Adjust position for turning
backwards_left(200, 1.9) #Turn to face mission
time.sleep(1)
move_backward(200, 0.5) #Move backwards so arm doesn't hit top of brush
right_attachment(500, 0.33) #Move attatchment down
move_forward(200, 1) #Move forward + hook the brush on
right_attachment(-300, 1) #Lift up arm + brush
