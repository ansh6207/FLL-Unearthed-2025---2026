import motor, time
from hub import port
import distance_sensor

# Ports
LEFT_MOTOR = port.D
RIGHT_MOTOR = port.C
DIST_SENSOR_PORT = port.B

# Settings
SPEED = 500
STEP_TIME = 0.1
BACKUP_TIME = 0.5
TURN_TIME = 0.6
OBSTACLE_THRESHOLD = 200# in mm

# Movement helpers
def move_forward(duration):
    motor.run(LEFT_MOTOR, SPEED)
    motor.run(RIGHT_MOTOR, -SPEED)
    time.sleep(duration)
    motor.stop(LEFT_MOTOR)
    motor.stop(RIGHT_MOTOR)

def move_backward(duration):
    motor.run(LEFT_MOTOR, -SPEED)
    motor.run(RIGHT_MOTOR, SPEED)
    time.sleep(duration)
    motor.stop(LEFT_MOTOR)
    motor.stop(RIGHT_MOTOR)

def turn_right(duration):
    motor.run(LEFT_MOTOR, -SPEED)
    motor.run(RIGHT_MOTOR, -SPEED)
    time.sleep(duration)
    motor.stop(LEFT_MOTOR)
    motor.stop(RIGHT_MOTOR)

# Main loop
while True:
    move_forward(STEP_TIME)

    # Read distance from the sensor
    distance = distance_sensor.distance(DIST_SENSOR_PORT)

    # If distance is valid and less than the threshold, avoid obstacle
    if distance != -1 and distance < OBSTACLE_THRESHOLD:
        move_backward(BACKUP_TIME)
        turn_right(TURN_TIME)
