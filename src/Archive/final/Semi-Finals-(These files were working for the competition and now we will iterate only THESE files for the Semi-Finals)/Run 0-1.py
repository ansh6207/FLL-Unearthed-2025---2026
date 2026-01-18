#Tip the Scale code
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

def backwards_right(speed, duration):
    motor.run(port.E, -speed)
    
    time.sleep(duration)
    motor.stop(port.E)

def backwards_left(speed, duration):
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

# Step 3: Code

# Come Toward Mission

move_forward(500, 2.84)

# Face Mission

turn_right(420, 1)

move_forward(100, 2)

# Do Misison

right_attachment(-400, 0.25)

# Come Home

move_backward(300, 0.6)

backwards_left(500, 0.7)

move_backward(1000, 1.6)
