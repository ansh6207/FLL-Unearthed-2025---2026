#Step 1: Imports
import motor, time, distance_sensor
from hub import port, sound

#Step 2: Functions

#Forward function
def move_forward_duration(speed, duration):
    #Starts motors
    motor.run(port.A, -speed)
    motor.run(port.E, speed)

    #Waits for duration time
    time.sleep(duration)

    #Stops motors
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

def left_extention(speed, duration): # left = up
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.C)

def right_extension(speed, duration): # right = down
    motor.run(port.D, -speed)
    time.sleep(duration)
    motor.stop(port.D)

def backwards_right(speed, duration):
    motor.run(port.E, -speed)

    time.sleep(duration)
    motor.stop(port.E)

def move_forward(speed, distance):
    #Make _distance the distance the sensor picks up from port B
    _distance = distance_sensor.distance(port.B)
    distance = distance * 10
    #Start a loop to go forward
    #While the distance from sensor is less than the distance we want - 30
    while _distance < (distance-30) :
        #Start motor to go forward
        motor.run(port.A, -speed)
        motor.run(port.E, speed)
        #Wait 0.001 seconds before checking distance
        time.sleep(0.001)
        #Update distance
        _distance = distance_sensor.distance(port.B)
        #Show current distance
        print("Distance is ", _distance)
    #Once the distance is correct, stop the motor
    motor.stop(port.A)
    motor.stop(port.E)

#Step 3: Code
#move forward and leave home
move_forward(600,95)
turn_left(400, 1.2)
move_forward_duration(200, 0.2)
turn_left(300, 0.2)
right_extension(700, 5)
backwards_right(400, 1.4)
move_forward(200, 120)
left_extention(-200, 2)
move_forward(600, 129)
left_extention(600, 1)
