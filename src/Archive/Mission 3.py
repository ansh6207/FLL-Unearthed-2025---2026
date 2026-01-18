import motor
import time
from hub import port

def left(speed, duration): #turn the robot left
    motor.run(port.E, speed)
    time.sleep(duration)
    motor.stop(port.E)

def right(speed, duration): #turn the robot right
    motor.run(port.A, -speed)
    time.sleep(duration)
    motor.stop(port.A)

def move(speed, duration): #move the attachment
    motor.run(port.C, speed)
    time.sleep(duration)
    motor.stop(port.C)

move(60,2.5) #ratio = 150
