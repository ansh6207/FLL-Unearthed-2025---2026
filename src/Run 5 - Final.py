# MicroPython classes        # Google: what is a python class
# here we only import parts    # Google: python what is importing?
# of the time object
from time import ticks_ms    # Google: python time.ticks_ms
from time import sleep        # Google: python time.sleep
from sys import exit


# spike classes
from hub import port            # Hub Port enums
from hub import motion_sensor
import motor
import motor_pair
from app import linegraph

import distance_sensor
import color_sensor
import color                    # color enums


import motor, time
from hub import port

SLEEP_MOTOR = 0.3


####################################################
# gyro drive globals
# Google: python global
####################################################

global Drive                                        # add any global settings

##################################################
# Gyro Drive Enum
# Associate a name with a number
##################################################
class log_level:
    OFF    = 0                                    # no normal log
    PROBLEM = 1                                    # only porblems
    END    = 2                                    # method end messages
    STEP    = 3                                    # method step messages
    START= 4                                    # method start messages
    ALL    = 5                                    # all general messages

class motor_velocity:
    SPIKE_SMALL_MOTOR= 660                        # definitions found under spike motor run method
    SPIKE_MEDIUM_MOTOR = 1110                    # see the Spike knowledge base to the right -->
    SPIKE_LARGE_MOTOR= 1050                        # add any others below

class results:                                    # larger numbers to see big deflects in the plot
    PROBLEM        = -1                        # If a problem happens. Will also throw an exception.
    CODE_RESET        = 0                        # this is reset at the beginning of the gyro_drive functions
    TARGET_REACHED    = 1                        # robot achieved the desired target
    WAYPOINT_DETECTED = 2                        # Did the robot see the optional waypoint?
    TIMED_OUT        = 3                        # gyro_drive reached the optional timeout
    RUNNING        = 4                        # This way if a mission failed, you can decided
                                                    # what you want the robot to do. Maybe drive back to base


####################################################
# main definition all python coode starts here
####################################################
def main():                                        # this is the main function. The code will flow top
                                                    # to bottom.

    global Drive, front_lift                        # Captures Drive and front_lift above as global in main

    # build the settings class, now called Drive.# there are other values that you manually set.
    Drive = gyro_drive_settings(5.57,            # wheel diameter, adjust as you need for accuracy
                                port.A,            # left motor port
                                port.E,            # right motor port
                                port.E,            # measure motor port, normally drives forward
                motor_velocity.SPIKE_MEDIUM_MOTOR)# motors max velocity, Knowledge Base

    Drive.logging_level = log_level.OFF            # will shut off logging, more to coem about my logging
    Drive.log_source_filter = 'LFLT'                    # defined a lof handle filter, '' is no filter.

    #Drive.use_linegraph = True                    # True turns on plotting if movement support this
    if Drive.use_linegraph == True:                # What does this say? easy to understand.
        linegraph.clear_all()                    # read about linegraph under app in Knowledge Base

    motor_pair.pair(Drive.motor_pair_id,            # Drive motors are assigned to motor_pair
                    Drive.motor_port_left,        # we use motor_pair on our drive motors
                    Drive.motor_port_right)        # with this we can start and stop them together.


    #################################################
    # if you need to power single motor you can
    # create versions of the spinny motor class
    #################################################
    right_spin = spinny('RTSP', port.D, 230,        # name, motor port, max_deg, all required
            motor_velocity.SPIKE_LARGE_MOTOR,    # max_vel(osity) required
                                                    # Optional settings, defaulted as shown
            accuracy=1,                            # How close to target is good? range is -1,0,1
            stop_mode=motor.SMART_BRAKE,            # What to do when you stop the motor.
            close_degrees=50,                    # How close to target do we go slow for accuracy.
            close_speed=10)                        # What speed to use when close.
                                                    # using default on all other options.

    left_lift = spinny('LFLT', port.C, 104,        # name, motor port, max_deg, all required
            motor_velocity.SPIKE_LARGE_MOTOR,    # max_vel(osity) required
                                                    # Optional settings, defaulted as shown
            accuracy=1,                            # How close to target is good? range is -1,0,1
            stop_mode=motor.SMART_BRAKE,            # What to do when you stop the motor.
            close_degrees=5,                    # How close to target do we go slow for accuracy.
            close_speed=10)                        # What speed to use when close.
                                                    # using default on all other options.

    #################################################
    # your code goes under here.
    # these can be movements or functions you create
    # when ready to use the tests, you comment out
    # your code.
    #################################################
    # these are just the calls, to your customized
    # functions. They are defined below the main method

    move_backward(515, 1.5) # move towards mission 1 and completes 1/3 of it
    #gyro_drive('d', target=41, speed=-100, request_angle=0)

    move_forward(600, 0.8) # completes other 1/3 of mission 1

    move_backward(600, 0.6) # just in case first soil deposit doesn't work

    backwards_left(455, 1.43) # turn towards mission 2

    gyro_spin_to_angle(140)

    left_lift.run(-102, 60, accuracy_override=1, close_degrees_override=80, close_speed_override=8) # puts arm down

    time.sleep(SLEEP_MOTOR)

    gyro_drive('d', 16) # move to revel one part of map

    time.sleep(SLEEP_MOTOR)

    turn_right(100, 0.29) # just in case, turn right

    turn_left(100, 0.2) # just in case, turn right

    left_lift.run(-90, 60, accuracy_override=1, close_degrees_override=80, close_speed_override=8)

    time.sleep(SLEEP_MOTOR) # motor wait
    
    gyro_spin_to_angle(163) # turn to go over to position over the sliding garden

    left_lift.run(-100, 50, accuracy_override=1, close_degrees_override=80, close_speed_override=8) # puts arm down

    time.sleep(SLEEP_MOTOR)

    gyro_drive('d', target=4.5, speed=10) # revels other part of map

    left_lift.run(-90, 50, accuracy_override=1, close_degrees_override=80, close_speed_override=8) # puts arm up

    time.sleep(SLEEP_MOTOR)

    gyro_spin_to_angle(180) #colect garden

    move_backward(400, 0.3)
    
    gyro_drive('s', target=76, speed=65) # move to revel one part of map

    gyro_spin_to_angle(270)

    gyro_drive('s', target=33, speed=40) # move to revel one part of map

    left_lift.run(-103, 60, accuracy_override=1, close_degrees_override=80, close_speed_override=8, async_op=True) # puts arm up

    #spinny.spin_multi_motors([left_lift])

    gyro_drive('d', target=26, speed=40, spinny_list=[left_lift])

    gyro_spin_to_angle(243)

    gyro_drive('d', target=3.45, speed=40)

    time.sleep(SLEEP_MOTOR)

    left_attachment(-100, 0.7)
    
    #left_lift.run(-5, 5, accuracy_override=5, close_degrees_override=80, close_speed_override=8, stop_mode_override=motor.BRAKE) # puts arm up slowly

    exit(0)

    ################################################################
    # end of main function.
    ################################################################



################################################################
# put your custom function definitions here
# create your own functions, then call them above
# These are examples. remove them is you wish
###############################################################

#Forward function


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





#################################################
# Gyro Drive classes, settings and functions
# Modify but do not remove
#################################################

class gyro_drive_settings():

    """
    This is a class that supports various tests
    to dial in your robot. These are a great
    teaching tool because the students can see
    what is happening. Then by walking the code
    the can see how it is done.

    Settigns from my testing
    wheel_diameter    = 8.85    # big 88 mm wheels,
    wheel_diameter    = 5.57    # small 56 mm wheels

    Why is 8.80 not working and you had to fuge it?
    This is a toy. After testing alot, these values
    worked on my robots. You will need to dial in
    yours.

    """

    ################################################
    # class initator do not touch
    ################################################
    # Warning: This code is executed when we
    # create the class. DO NOT CHANGE ANY OF
    # the variables below once program starts.
    ################################################
    def __init__(self,
        wheel_diameter,
        motor_port_left,                                # use port. definitions
        motor_port_right,
        measure_motor_port,
        motor_max_velocity):

        self.wheel_diameter = wheel_diameter
        self.motor_port_left = motor_port_left
        self.motor_port_right = motor_port_right
        self.measure_motor_port = measure_motor_port
        self.motor_max_velocity = motor_max_velocity

        # distance calcs                                # do not remove these
        Pi                = 3.14159                    # Thank you Archimedes of Syracuse for Ï€
        self.wheel_circumference = \
            Pi * float(self.wheel_diameter)            # all them Greeks knew about it

        self.distance_per_degree = \
            self.wheel_circumference / 360            # how far do we go in 1 degree of movement
                                                        # think of it a distance around a pizza slice
                                                        # if cut into 360 slices.

                                                # Google: python ticks_ms
    program_started_sec = ticks_ms()/1000    # ticks_ms() capture the start moment in milliseconds
                                                # /100    divide by 1000 to get seconds decimal.
                                                # ticks_ms starts from 0 when you turn on the hub.
                                                # If you leave the robot on it will rollover to 0
                                                # after 298 days. Try not to leave you hub on
                                                # for that long. :)
    ###########################################
    # All the code below can be changed after
    # the class is created using the form
    # Drive.blabla = blabla
    # Make sure you do this where all can see
    # it in case they are relying on this value
    ###########################################

    # one motor must run in reverse            # we multiply velocity * -1 to invert that motor
    motor_left_direction = -1                # normally flipped (-1)
    motor_right_direction = 1                # normally runs forward (1).

    motor_pair_id = motor_pair.PAIR_3        # there are 3 possible motor_pairs
                                                # we are using PAIR_3. This allows
                                                # us to assign the lef a right drive
                                                # motors to a motor_pair. Then the
                                                # motors are started/stopped together.

    distance_sensor_port = port.B                # must be set when using distance sensor
    distance_sensor_accuracy = .3            # how close to target is good? +/- this

    color_sensor_port    = -1                # must be set when using color sensor

    # test these spin settings to fit your robot.
    spin_far_range    = 30                    # degrees from target where we spin fast
    spin_far_speed    = 35                    # when range is > spin_far_range, spin faster
    spin_near_speed    = 8                    # when range is <= spin_far_range near, spin slow

                                                # stop at within spin_accuracy
    spin_accuracy    = 2.0                # we are on target+/- this accuracy
                                                # the robot has momentum and robot can't stop
                                                # on a dime so we make accuracy wide.
                                                # This gives the code time to stop the spin
                                                # close to the angle we want.
                                                # Students learn about tradeoffs.

    # speed defaults - experimant on your design.
    # you do not need to use these
    # just here as suggestions.
    default_speed        = 70                    # you set to what you want.
                                                # use Drive.default_speed in functions to use this
    default_rev_speed= default_speed        # determine this by testing.

    min_speed            = 12                    # minimum drive speed so we don't get stuck
                                                # gyro_drive asks for speed. As we get close
                                                # the speed man be very low. This will be the
                                                # minimum. Hey, robot has to move, right!!!
                                                # speed is 0 to 100 percent of max velocity.

    settle_time        = .20                    # once we reach the target, pause to let the robot settle
                                                # a heavier robot may need a little more time

    # gyro yaw settings
    use_yaw_360        = True                # if True get_yaw will allow you to use angles from
                                                # 0 to +/- 540. However, you can cross +/- 180 and +/- 360.
                                                # you need to be careful around +/- 540


    yaw_adjust        =.7                # A multiplier to adjust your motors to move back to the
                                                # gyro heading when we are using the gyro.
                                                #.5 one half of correction, gentle nudge works best
                                                # 1.0 is no additional adjustment, correction is applied as is
                                                # heavy robots may need more to move back to gyro line.
                                                # 2.0 will give you 2 times adjustment power
                                                # 3.0 will give you 3 times adjustment power
                                                # Warning: Too munch and you get overcorrection
                                                # Google: overcorrection

    # acceleration parameters
    accel_ramp_up_dist_pct= .12            # this is multipled by speed to figure out
                                                # how large to make the ramp up and down distance.

    accel_min_ramp_up_dist= 1.5            # minimum ramp up distance. 2.0 cm is 4/5 of an inch.



    use_linegraph    = False                # set to True to see linegraph of gyro drive

    result_code = results.CODE_RESET            # global var Drive.result_code to track function results.
                                                # mostly used the overrides like timeout and waypoint.
                                                # shows up as yellow in plots

    last_distance_cm = 0                        # how far Gyro_drive went the last time out in cm
                                                # updated every time gyro_drive finishes moving

    pass_count = 0                            # how many pass through the code
    gyro_drive_passes = 0

    logging_level = log_level.ALL            # what log level will we print

    log_source_filter = ""                    # no display filters, display all
    #log_source_filter = "GETY"                # display only these logs



#################################################
# Gyro Drive functions
# Modify but do not remove
#################################################


def gyro_drive( drive_by,                            # d = distance, t = time (sec), s = sonar
                target,                              # distance or time
                speed = 70,         # % of power +/- 10 to 100
                request_angle = None,                # angle to follow +/- 540. See get_yaw
                                                     # if None, gyro correction and turn_first are ignored

                timeout=None,                        # time sec to stop is not completed.
                waypoint = None,                        # color to look for. Will stop at the color.
                spin_left=False,                        # set True to spin left avoiding objects on the right
                spin_right=False,
                spinny_list = []):                    # set True to spin right avoiding objects on the left

    global Drive                                        # all the variable in Drive class available here.
                                                        # defined at the top of main

    current_reading = 0                                # gyro drive current sensor reading
                                                        # do not manually change
                                                        # type d, distance in centimeters
                                                        # type t, elapsed time
                                                        # type s, sonar distance in centimeters
    #Drive.logging_level = log_level.ALL

    yaw = actual_yaw = 0                                # set here so no errors down below
                                                        # yes this is ok
    if Drive.use_linegraph == True:
        gyro_drive_plot(speed, target, request_angle,
                result_code = Drive.result_code )

    if request_angle is not None:                    # In None gyro nav is off.
        gyro_spin_to_angle(request_angle,            # point us in the new direction first before driving
                            spin_left,                # if true force spin left, up to operator
                            spin_right)                # if true force spin right, up to operator

        yaw, actual_yaw = get_yaw(request_angle)        # get yaw returns 2 items always




    ''' Explain: Drive_by is a string
        Strings are a list of characters. Google: python list
        We hope drive-by will contain d for distance, t for time,
        or s for distance sensor
        drive_by[0] Take the first character in string drive_by
        [0].lower() converts to lower case character for testing
    '''
    # clean up this just in case
    drive_by = drive_by.strip()                            # remove all spaces around it. Google: python strip
    if len(drive_by) == 0: drive_by = 'd'                # if now blank, force to d for distance
    drive_by = drive_by[0].lower()                        # take first character [0] and force to lower

    motor.reset_relative_position(Drive.measure_motor_port,0) # before we drive, reset the measure motor start point
    result_code = results.CODE_RESET                        # Reset here becasue turn_to_angle will set it.
    Drive.last_distance_cm = 0                            # this will be how far we traveled when gyro_drive finishes.

    # Make sure we can at least move                        # too low, no movement. Adjust for you robot weight
    if abs(speed) < Drive.min_speed:                        # are we below minimum speed in either direction
        if speed < 0:
            speed = Drive.min_speed * -1                    # reverse the drive
        else:
            speed = Drive.min_speed                        # leave it forward

    calc_speed = 0                                        # declared here so we do not have hightights below
    color_sensor_reading = None                            # define here so we have no highlighte below

    function_started_sec = get_hub_sec()                    # local function timer vs Drive.program_started_sec


    passes = 0
    while True:                                            # loop forever, we need to break out or return out
        passes += 1

        local_elapsed_sec = \
            get_elapsed_sec(function_started_sec)        # subtracts current seconds from when function started

        if timeout is not None and \
                        local_elapsed_sec > timeout:        # is there a timeout and did we expire it
            motor_pair.stop(Drive.motor_pair_id,
                                stop=motor.SMART_BRAKE)    # stop the robot by locking motors, no roll
            Drive.result_code = results.TIMED_OUT        # set the Drive.result_code

            if Drive.use_linegraph == True:
                gyro_drive_plot(speed, target,
                        result_code = Drive.result_code,
                        color_reading = color_sensor_reading,
                        last_step = True)

            time.sleep(Drive.settle_time)                        # allow robot to settle, greatly improves accuracy

            # remeber how many cm's we traveled
            Drive.last_distance_cm = \
                int(abs(motor.relative_position(Drive.measure_motor_port)
                        * Drive.distance_per_degree))        # calculate the distance.

            log(log_level.END,
                'GYDR', " | Done",
                ' | drive_by: ', " option: timeout",
                ' | result_code: ', get_result_code_text(),
                ' | passes: ', passes)

            return

        # are we looking for a waypoint color?
        if waypoint is not None:                            # this is an optional parameter,
                                                            # if not None we do something
            color_sensor_reading = \
                color_sensor.color(Drive.color_sensor_port) # this may be highlighted if no color sensor
                                                            # port is defined.That is ok.

            if color_sensor_reading == waypoint:            # did the color sensor see the color we want
                motor_pair.stop(Drive.motor_pair_id,
                                    stop=motor.SMART_BRAKE)

                Drive.result_code = results.WAYPOINT_DETECTED# set the Drive.result_code

                if Drive.use_linegraph == True:
                    gyro_drive_plot(calc_speed, target,
                            result_code = Drive.result_code,
                            color_reading = color_sensor_reading,
                            last_step = True)

                time.sleep(Drive.settle_time)                    # allow robot to settle, greatly improves accuracy

                Drive.last_distance_cm = \
                    int(abs(motor.relative_position(Drive.measure_motor_port)
                            * Drive.distance_per_degree))

                log(log_level.END,
                    'GYDR', " | Done",
                    ' | drive_by: ', " option: waypoint color",
                    ' | result_code: ', get_result_code_text(),
                    ' | passes: ', passes)

                return                                    # Get out of this function, Google: python return
        else:
            color_sensor_reading = None

        ######################################################
        # Begin if / else ladder or decision tree
        ######################################################
        if drive_by == 'd':                                # Is this drive by distance?

            current_reading = \
                abs(motor.relative_position(Drive.measure_motor_port)
                        * Drive.distance_per_degree)        # calculate the distance.

            log(log_level.STEP,
                    'GYDR', " | Done",
                    ' | drive_by: ', drive_by,
                    ' | result_code: ',
                        get_result_code_text(),
                    ' | target distance: ',
                        current_reading,
                    ' | passes: ', passes)

            if current_reading >= abs(target):
                motor_pair.stop(Drive.motor_pair_id,
                                    stop=motor.SMART_BRAKE) # drives will stop together.
                Drive.result_code = results.TARGET_REACHED# set the Drive.result_code

                if Drive.use_linegraph == True:
                    gyro_drive_plot(calc_speed,            # plot the final results
                        current_reading,
                        target,
                        result_code = Drive.result_code,
                        color_reading = color_sensor_reading)


                time.sleep(Drive.settle_time)                    # allow robot to settle, greatly improves accuracy

                Drive.last_distance_cm = \
                    int(abs(motor.relative_position(Drive.measure_motor_port)
                            * Drive.distance_per_degree))


                log(log_level.END,
                    'GYDR', " | Done",
                    ' | drive_by: ', drive_by,
                    ' | result_code: ',
                        get_result_code_text(),
                    ' | target distance: ',
                        current_reading,
                    ' | passes: ', passes)


                return                                    # Get out of the function, Google: python return

            calc_speed = acceleration(target,
                                    speed,
                                    current_reading,
                                    Drive.accel_ramp_up_dist_pct,
                                    Drive.min_speed)        # pass min_speed from Drive settings


        elif drive_by == 't':                            # processign a travel over time
            calc_speed = speed


            log(log_level.STEP,
                'GYDR', " | Done",
                ' | drive_by: ', drive_by,
                ' | result_code: ',
                    get_result_code_text(),
                ' | elapsed sec: ',
                    local_elapsed_sec,
                ' | passes: ', passes)


            if local_elapsed_sec >= target:                # are we sat the requested time>
                motor_pair.stop(Drive.motor_pair_id,
                                    stop=motor.SMART_BRAKE)
                Drive.result_code = results.TARGET_REACHED

                if Drive.use_linegraph == True:
                    gyro_drive_plot(calc_speed,            # plot the final results
                        local_elapsed_sec,
                        target,
                        result_code = Drive.result_code,
                        color_reading = color_sensor_reading)


                time.sleep(Drive.settle_time)                    # allow robot to settle, greatly improves accuracy

                Drive.last_distance_cm = \
                    int(abs(motor.relative_position(Drive.measure_motor_port)
                            * Drive.distance_per_degree))

                log(log_level.END,
                    'GYDR', " | Done",
                    ' | drive_by: ', drive_by,
                    ' | result_code: ',
                        get_result_code_text(),
                    ' | elapsed sec: ',
                        local_elapsed_sec,
                    ' | passes: ', passes)
                return                                    # Get out of function, Google: python return


        elif drive_by == 's':
            current_reading = \
                distance_sensor.distance(
                        Drive.distance_sensor_port) * .1    # distance comes in as integer milimeters
                                                            # mult by .1 changes it to float centimeters
            closing_speed = speed

            log(log_level.STEP,
                'GYDR', " | Done",
                ' | drive_by: ', drive_by,
                ' | result_code: ',
                    get_result_code_text(),
                ' | current distance: ',
                    current_reading,
                ' | target distance: ',
                    target,
                ' | passes: ', passes)

            if current_reading >= \
                target - Drive.distance_sensor_accuracy and \
                current_reading <= \
                target + Drive.distance_sensor_accuracy:    # are we close to the target distance

                motor_pair.stop(Drive.motor_pair_id,
                                stop=motor.SMART_BRAKE)
                Drive.result_code = results.TARGET_REACHED# set the Drive.result_code

                if Drive.use_linegraph == True:
                    gyro_drive_plot(closing_speed,        # plot the final results
                        current_reading,
                        target,
                        result_code = Drive.result_code,
                        color_reading = color_sensor_reading)

                time.sleep(Drive.settle_time)                    # allow robot to settle to improve accuracy

                Drive.last_distance_cm = \
                    int(abs(motor.relative_position(Drive.measure_motor_port)
                            * Drive.distance_per_degree))

                log(log_level.END,
                    'GYDR', " | Done",
                    ' | drive_by: ', drive_by,
                    ' | result_code: ',
                        get_result_code_text(),
                    ' | current distance: ',
                        current_reading,
                    ' | target distance: ',
                        target,
                    ' | passes: ', passes)
                return                                    # We reached the target! Google: python return

            elif current_reading < target:                # too close back up
                calc_speed = closing_speed
            elif current_reading > target:                # go closer
                calc_speed = -closing_speed

        else:
            raise( Exception( "gyro_drive: tdrive by type not d, t, or s!'") )

        # Endif / else ladder of decisions

        # now drive based upon what was set above.
        # this return a 2 value tuple. You can catch them a a tuple
        # or as we did there as the 2 seperate values.
        left_velocity, right_velocity = \
            calc_drive_velocities( calc_speed, request_angle,# returns velocities as a tuple!!!! Has 2 values
                            Drive.motor_max_velocity,
                            Drive.yaw_adjust )

        motor_pair.move_tank(Drive.motor_pair_id,            # forces motors to start together.
                            left_velocity,                    # left
                            right_velocity)                    # right

        if Drive.use_linegraph:
            gyro_drive_plot(calc_speed,                        # plot where we are
                        current_reading,
                        target,
                        result_code = Drive.result_code,
                        color_reading = color_sensor_reading)

        if len(spinny_list) > 0:
            spinny.spin_multi_motors(spinny_list, async_op=True)


def gyro_drive_plot(speed,
                    current = None,                            # if None, do not plot
                    target = None,
                    result_code = None,
                    color_reading = None,
                    last_step = None):

    global Drive                                                # give us access to the settings

    elapsed = get_elapsed_sec( Drive.program_started_sec)    # calc elapsed time from program start

    linegraph.plot(color.RED,    elapsed,speed)
    yaw, actual_yaw = get_yaw()
    linegraph.plot(color.PURPLE, elapsed,yaw)                # yaw reading
    linegraph.plot(color.MAGENTA, elapsed, actual_yaw)

    if current is not None:
        linegraph.plot(color.GREEN, elapsed, current)        # current position, reading whaever

    if target is not None:
        linegraph.plot(color.BLUE,elapsed, target)            # were are we going?

    if color_reading is not None:                            # color sensor reading
        linegraph.plot(color.BLACK, elapsed, color_reading)

    if result_code is not None:
        linegraph.plot(color.YELLOW, elapsed, result_code )

    if last_step is not None:
        linegraph.plot(color.ORANGE, elapsed, 3)                # mark the end of a movement


def get_yaw(request_angle = 0.0, raw=False ):

    global Drive

    """
    Returns the yaw from the motion hub sensor.
    We cook it to spoof (trick) it to work through
    +/-180 degrees and +/-360 degrees.

    This is done by looking at the request_angle passed.
    The spoofing will make so the yaw will support the
    passing beyond 180 degrees.

    Parameters:
    request_angle (float): Angle you are trying to turn to.

    raw :        Boolean (True/False) to use the the uncooked
                raw yaw value. Otherwise we use round(yaw).
                This helps when you have a drfiting gyro value.
                We may not need this as we have figured out
                How to correct that.

    Example:    yaw, actual_yaw = get_yaw(request_angle)



    Returns: WARNING: This always return 2 values called
            a tuple. The 2 values are the spoofed yaw
            and the actual_yaw from the motion sensor.

    """

    log(log_level.START, 'GETY' ,
            ' | req_angle: ', request_angle,
            ' | raw: ', raw )

    robot_angles = motion_sensor.tilt_angles()            # this returns a tuple. Google: python tuple
                                                            # The tuple robot_angles has all our angles.

    if raw == True:
        yaw = (robot_angles[0]/10)                        # raw no rounding
    else:
        yaw =round((robot_angles[0]/10))                    # [0] is the first item in the tuple. Yaw is an
                                                            # int of decidegress. We divide by 10 to get degrees.
                                                            # This is now a float or decimal. We round it to
                                                            # improve movement.

                                                            # In Spike Python left yaw is positive, right negative
    yaw = yaw * -1                                        # We want to make it the same as Blocks, so we flip it
                                                            # now left is -, and right is +.

    request_angle = int(request_angle)                    # MicroPython likes integers.

    actual_yaw = yaw                                        # save the actual yaw as actual_yaw

    if Drive.use_yaw_360 == False:                        # Use +/- 180 degree compass

        log(log_level.END, 'GETY' ,
            ' | req_angle: ', request_angle,
            ' | raw: ', raw,
            ' | actual_yaw: ', actual_yaw,
            ' | yaw: ', yaw)

    else:                                            # Use +/- 360 degree compass

        op = 0                                        # tell us what operation was used

        # spinning left, negative direction
        if request_angle < -135:                        # -135 allows clean movement over -180 degrees.

            op = 1                                    # this takes us from -0 to -180
                                                        # just show the yaw no change to yaw

            if request_angle < -315 and \
                yaw <= 0 and yaw < 180:                # ensure clean past -360 to -540
                    yaw = -360 + yaw                    # yaw between 0 and 180
                    op = 13

            elif yaw < -180:                            # not sure this does anything
                op = 11
                yaw = yaw + 360

            elif yaw > 0 and yaw < 180:                # support -180 passingto -360
                op = 12                                # now yaw is 179 to 1
                yaw = (360 - yaw) * -1                # yaw < 180360-179 = 181 * -1 = -181

        # spinning right, positive direction
        elif request_angle > 135:                    # all below happens if we are 135 or higher
            op = 2 # this takes us from 135 to 180    # 135 allows clean movement over 180 degrees.

            if request_angle > 315 and \
                yaw >= 0 and yaw <= 180:                # override to 540 when we req_angle > 315
                                                        # set up to spin to +540 degrees 180+360=540
                yaw = yaw + 360                        # we start at 360 and add yaw up to 180
                op = 23                                #0 + 360 = 360,1 + 360 = 361,
                                                        # 90 + 360 = 450, 180 + 360 = 539
                                                        # range up to 540

            elif yaw > 180:                            # not sure this does anything
                op = 21                                # yaw cannot be > 180
                yaw = yaw - 360

            elif yaw < 0 and yaw >= -180:            # Are we between -179 and -1
                op = 22
                yaw = (yaw + 360)                    # add yaw to 360, we extend 180 to 181, 182...
                                                        # -179 + 360 = 181, -178 + 360 = 182
                                                        # range is up to 360



        if op == 21 or op == 11:
            log(log_level.END, 'GETY' ,
                ' | req_angle: ', request_angle,
                ' | raw: ', raw ,
                ' | op:', op,
                ' | hub yaw: ', actual_yaw ,
                ' | calc yaw: ', yaw )


    return yaw, actual_yaw                            # return both yaws. User chooses



def calc_drive_velocities( speed,
                        request_angle,                # angle can be None. This turns off gyro navigation
                        max_velocity,
                        yaw_adjust = 1.0):

    '''
    We created this so you can use it in your own drive functions.
    This is desiogned to take a max velocity and a speed% along with
    the requested angle and return the gyro corrected velocities.

    if request_angle is None then the velocities will be the same
    reflecting no gyro correction.

    parameters:
        speed - your motor speed
        request_angle - what angle you want to steer. None turns off gyro nav.
        max_velocity - the maximum velosity of the motor as define in spike
                    for small, medium and large LEGO motors.
        yaw_adjust - this value is used to give more for the the correction of yaw.
                    it is defaulted to 1. If you do not put in the parameter it wil be 1.

    In Blocks gyro.yaw comes in as - when turning left and + when turning right
    In Python gyro.yaw comes in as + when turning left and - when turning right
        Note: We adjusted our python function get_yaw() to force yaw to be flipped to
                match what happens in Blocks so, - is left, + is right.
    '''

    if request_angle is None:                                    # no navigation requested
        yaw_correction = 0
        yaw = 0
    else: #request_angle is not None
        yaw, actual_yaw = get_yaw(request_angle)                    # always capture both

        yaw_correction = (request_angle - yaw)                    # this is how much we are off + right, - left

    left_speed= speed + yaw_correction                            # apply the correction to the speed
    right_speed = speed - yaw_correction                            # opposite to bring you back

    left_velocity =int(calc_pct_value(max_velocity,left_speed)) # calculate the velocity from the speed
    right_velocity = int(calc_pct_value(max_velocity,right_speed))

    log(log_level.END, "CDVL",
            " | req_angle: ", request_angle,
            ' | speed: ', speed,
            ' | yaw: ', yaw,
            ' | corection: ', yaw_correction,
            ' | speeds (l/r): ', left_speed, '/', right_speed )

    return left_velocity, right_velocity                            # return the 2 velocities as integers
                                                                    # returning 2 items creates a tuple
                                                                    # Google: what is a python tuple



def acceleration( tot_distance, speed, curr_distance,
            accel_ramp_up_dist_pct = .10,
            accel_min_speed = 5,
            reverse_ramp_up_speed = 40):

    """
    Calculates the acceleration, steady state and
    decelleration of your robot. It is callled by
    others passing the appropriate parameters.

    Parameters:
    tot_distance (int):Total distance you want to go

    speed (int):        Percent of speed +/- 0 to 100

    curr_distance (int): How far you have gone in distacne so far

    accel_ramp_up_dist_pct (float): multiplied against speed
                        to calculate the ramp up distance.
                        defaults to .10

    accel_min_speed (int): Minimum speed to be sure we
                        get to the end

    Returns:
    Calculated speed at this point over the distance

    """

    if accel_ramp_up_dist_pct == 0:                                # turn off acceleration
        return speed

    ramp_up_dist = accel_ramp_up_dist_pct * abs(speed)            # This produces a percent we use
    if ramp_up_dist < Drive.accel_min_ramp_up_dist:                # to calc ramp up distance
        ramp_up_dist = Drive.accel_min_ramp_up_dist                # 2 cm default. Less than 1 inch
                                                                    # distance that will be the ramp up
                                                                    # distance?Why?

    # Capture the direction
    if speed < 0:
        direction = -1                                            # reverse, negitive direction
    else:
        direction = 1                                            # forward, positive direction

    # we have direction so all calculations
    # are now done using abs. We are positive now
    curr_distance = abs(curr_distance)                            # Google: abs or absolute value.
    speed = abs(speed)

    if speed < accel_min_speed:
        speed = accel_min_speed                                    # make sure we can move

    # calculate the ramp up and down distances
    ramp_pct_traveled = 0                                        # starting from the beginning

    #ramp_up_dist = tot_distance * accel_ramp_up_dist_pct            # ramp_up distance is how far
                                                                    # will we ramp up the speed

    ramp_down_dist = ramp_up_dist * 2                            # ramp down twice as big for slowing down
    ramp_down_start_dist = tot_distance - ramp_down_dist            # where does ramp down start?

    if abs(speed) < abs(reverse_ramp_up_speed):                    # if reversing fast, make ramp up tripple in size
        ramp_up_dist *= 3                                        # this may help prevent wheel slip, test!!!!!

    log(log_level.START, 'ACEL',
                        " | speed:" + str(speed),
                        " | curr_dist:" + str(curr_distance),
                        " | ramp_up:" + str(ramp_up_dist),
                        " | ramp_dn:" + str(ramp_down_start_dist) )



    ################################################################
    # Now we need to decide what to do.
    # what part of the run are we in.
    # This is called an if / else ladder.
    ################################################################
    # are we passed the total distance?
    if curr_distance >= tot_distance:                            # if done return 0 speed.
        log(log_level.END, 'ACEL',
                " | Done ",
                " | curr_distance: " , curr_distance,
                " | tot_distance:" , tot_distance)

        return 0                                                    # we are where we want to be.
                                                                    # length or distance is never negative.

    # Are we in ramp down mode?                                    # down mode takes priority, why?
    elif curr_distance > ramp_down_start_dist:                    # Is the distance within the ramp_down?
        curr_ramp_dist = curr_distance - ramp_down_start_dist    # get the distance in ramp_down area only, not total
        ramp_pct_traveled = curr_ramp_dist / ramp_down_dist        # get the percentage in the ramp_down distance

        # unlike ramp up, we are in ramp down, we slow down        # nice chance for thought experiment!!!
        pct_slowing = (1.0 - ramp_pct_traveled)                    # this will go from 1.0 to .00, slowing down
                                                                    # .10 is now .90, .25 is now .75
        calc_speed = speed * pct_slowing                            # Calculate the new slowing speed

        if calc_speed <= accel_min_speed:                        # check that we are minimum speed
            calc_speed = accel_min_speed                            # if not we may not move at very slow speeds

        calc_speed *= direction

        log(log_level.END,
                'ACEL',
                " | Ramp Down ",
                " | direction: " , direction,
                " | calc_speed:" , calc_speed,
                " | curr_ramp_pct_trav:", ramp_pct_traveled ,
                " | pct_slowing:" , pct_slowing)


        return calc_speed                                        # convert back to the direction

    # Are we in ramp up mode?
    elif curr_distance < ramp_up_dist:                            # Is the distance within the ramp_up?
        ramp_pct_traveled = curr_distance / ramp_up_dist            # get the percentage of the ramp up distance

        calc_speed = speed * ramp_pct_traveled                    # calculate the speed within the ramp up distance
                                                                    # we are speeding up, pct .0 to 1.0

        if calc_speed <= accel_min_speed:                        # check that we are at minimum speed
            calc_speed = accel_min_speed                            # if not, we may not move at very slow speeds

        calc_speed *= direction

        log(log_level.END, 'ACEL',
            " | Ramp Down ",
            " | direction: " , direction,
            " | calc_speed:" , calc_speed,
            " | curr_ramp_pct_trav:" ,
                ramp_pct_traveled )



        return calc_speed

    # are we in steady state mode?
    elif curr_distance >= ramp_up_dist and \
                    curr_distance <= ramp_down_start_dist:

        calc_speed = speed * direction

        log(log_level.END,
            'ACEL',
            " | Steady State ",
            " | direction: " , direction,
            " | calc_speed:" , calc_speed,
            " | curr_distance:", curr_distance )

        return calc_speed

    else:                                                        # in case something is broken, tell us!!!
        print("except, curr_dist:" + str(curr_distance)
                        + ", up_d:" + str(ramp_up_dist)
                        + ", dn_d:" + str(ramp_down_start_dist))

        raise(Exception("acceleration: no ramp calculated!!!!"))



def get_hub_sec():
    '''
    The function ticks_ms is imported above from the python time module
    it returns miliseconds since the robot was turned on.
    It rolls over in 200+ days so we are good.

    Google: micropython ticks_ms
    Google: What are milliseconds?
    '''
    ms = ticks_ms()                                                #capture as milliseconds. It is an integer, no decimal

    '''
    Google: What is a python integer
    Google: What is a python float or floating point number
    Google: python float function
    convert and return as a float
    now representing seconds, with decimals, since the robot started.
    '''
    return float(ms)/1000                                        # convert to a float and divide by 1000
                                                                    # now we can do normal math on it.
                                                                    # return a float in seconds.

def get_elapsed_sec(start_seconds):
    '''
    Returns the total elpased time from a passed start time.

    parameters:
        start_seconds - when caller started timing from.
                        Users mus captru a start point.
                        Example: start_point = get_hub_sec()

    This allows you to determine elapsed time from a function or
    from when the program started. It depends on what
    start_seconds you pass.
    '''

    return get_hub_sec() - start_seconds


def calc_pct_value(max_value, range_value):

    '''
    calc_pct_value(max_value, range_value):
        This converts a range +/- 100 into a value you want from a
        max value for that device.

        Example: Convert the speed to whatever velocity system you are using.
        In Spike we have 3 different motors and each have a different max
        velocity. Spike Python tools native velocity is degrees per second.

        That is not very easy for a carbon based unit (middle schooler) to grasp.
        Here you can provide speed as range_value which is simply
        percent range of +/- 100. It is very simple to understand and
        matches what block uses.

        A speed of 25 becomes .25, 50 becomes .5, 100 becomes 1.0
        Then we multiply max_velocity by speed to get requested velocity.
        Easy peasy. Very technical term.
    '''

    pct_value = range_value *.01                                # convert int range_value to float pct_value
                                                                # now a decimal. 50 becomes .50 or 1/2

    calc_value = max_value * pct_value                        # multiply max_value by pct_value

    return( calc_value)                                        # return calc_value
                                                                # return a float for better precision
                                                                # if max is 1000, 1000 * .50 = 500(1/2)
                                                                # receiver can convert to int if they need it.


def gyro_spin_to_angle(request_angle, spin_left=False, spin_right=False):

    """
    gyro_spin_to_angle(request_angle, spin_left=False, spin_right=False):
        Spins the robot to the requested angle.
        It can be called by itself or from
        gyro_drive. We say spin becasue the robot
        will normally spin on the center of the robot,
        over the wheels.

        If it completes normally, it will set
        Drive.result_code to results.TARGET_REACHED

        Parameters:
        request_angle (float): The angle you want
            degrees +/-360. We will calc actual_yaw from it.
        spin_left: If True forces robot to spin left, default False
        spin_right: If True forces robot to spin right default False

        Returns:
        Nothing

    """

    global Drive

    Drive.result_code = results.CODE_RESET
    speed = 0                                            # usable everywhere below.


    if request_angle is None:
        Drive.result_code = results.PROBLEM
        log(log_level.END, 'GSTA',
            " | req_angle is None: Returning!!!" )
        return

    log(log_level.START, 'GSTA',
        " | req_angle:", request_angle,
        " | spin_left:", spin_left,
        " | spin_right:", spin_right )

    while True:
        yaw, actual_yaw = get_yaw(request_angle)
        correction = request_angle - yaw                # how far off request_angle are we

        # are we there yet!!!!
        if abs(correction) <= Drive.spin_accuracy:    # are we within accuracy
            motor_pair.stop(Drive.motor_pair_id ,
                                    stop=motor.HOLD)    # hold will activly hold position
            time.sleep(Drive.settle_time)

            log(log_level.ALL, 'GSTA',
                " | request_angle: ", request_angle,
                " | actual_yaw:", actual_yaw,
                ' | yaw:', yaw,
                " | corr: ", correction,
                " | speed: ", speed)
            break                                    # get out of the loop, we are there.

        turn_text = 'Unk'                            # shows the decision, right/left

                                                        # spinning is oposite of going straight
        if spin_right == True:                        # to spin right, right goes in reverse,
            turn_direction = -1                        # left in forward
            turn_text = 'force-right'
        elif spin_left == True:                        # to spin left, left goes in reverse,
            turn_direction = 1                        # right goes forward
            turn_text = 'force-left'
        elif correction >= 0:                        # we want to go right
            turn_direction = -1                        # spin right, right goes backward
            turn_text = 'right'
        else:
            turn_direction = 1                        # we want to go left
            turn_text = 'left'                        # spin left, left goes backward

        if abs(correction) > Drive.spin_far_range:    # how far from target can we spin fast
            spin_speed = Drive.spin_far_speed        # we are far from target, spin fast
        else:
            spin_speed = Drive.spin_near_speed        # we are near target, slow down

        speed = spin_speed * turn_direction            # apply direction to our speed.

        log(log_level.ALL, 'GSTA',
            " | req_angle:", request_angle,
            " | actual_yaw:", actual_yaw,
            " | yaw:", yaw,
            " | turn:" , turn_direction,
                    "(", turn_text,')',
            " | cor:", correction,
            " | speed:", speed)


        velocity = int(
            calc_pct_value(Drive.motor_max_velocity,    # calc the velocity, make it an int
                        speed))

        motor_pair.move_tank(Drive.motor_pair_id,    # apply velocities to the motors
            velocity * Drive.motor_left_direction ,    # we use motor_pair so they start
            velocity * Drive.motor_right_direction)# and stop, together

    time.sleep(Drive.settle_time)                            # let robot settle, it is moving
    #if Drive.use_linegraph == True:
    #    gyro_drive_plot(correction, yaw, angle, last_step = True)
    Drive.result_code = results.TARGET_REACHED
    log(log_level.ALL, 'GSTA'," | Target Reached")

    yaw, actual_yaw = get_yaw(request_angle)            # get the yaw to see where we ended.

    log(log_level.END, 'GSTA',
        " | request_angle: ", request_angle,
        " | actual_yaw: ", actual_yaw,
        " | corr: ", correction,
        " | yaw ", yaw,
        " | spin_left:", spin_left,
        " | spin_right:", spin_right,
        " | speed:", speed )


def get_result_code_text():

    if Drive.result_code == results.CODE_RESET:
        code_text = 'Result Code Reset (' + str(Drive.result_code) + ')'

    elif Drive.result_code == results.TARGET_REACHED:
        code_text = 'Target Reached (' + str(Drive.result_code) + ')'

    elif Drive.result_code == results.TIMED_OUT:
        code_text = 'Timed Out (' + str(Drive.result_code) + ')'

    elif Drive.result_code == results.WAYPOINT_DETECTED:
        code_text = 'Waypoint Detected (' + str(Drive.result_code) + ')'

    else:
        code_text = 'Unknown Code (' + str(Drive.result_code) + ')'

    return code_text



def log(msg_level, source, *args):                    # args is the rest of the vales.

    if Drive.log_source_filter != "":                # are there any source filters?
        if Drive.log_source_filter.find(source) < 0:    # do not show this source
            return                                    # get out

    if msg_level <= Drive.logging_level:                # show an below the level
                                                        # notice the order of the list.
        levels = ["OFF", "PROBLEM", "END", "STEP",
            "START", "ALL"]

        # get he message type, may be unknown
        try:                                            # we try
            level_name = levels[msg_level] + '.' * 5
        except:                                        # problem?
            level_name = 'UKNOWN - See levels'        # we do this

        level_name = level_name[:5]                    # strip level to only 4 characters


        # format the time stamp common look    .        # string manipulation is cool!!!
        tyme = str(get_elapsed_sec(Drive.program_started_sec)) # get the elapsed sec
                                                        # example: "5.34" string!!!
        parts = tyme.split('.')                        # split on . to get sec and mills
                                                        # parts is a list ["5","34" ]
        sec = "    " + parts[0]                        # sec now = "    5"
        ms = str(parts[1] + '00000')                    # ms now= "3400000"
        tyme = sec[-5:] + '.' + ms[:3]                # glue back together
                                                        # "5.340" so nice!!!


        message = tyme + ' | ' + str(source)\
                    + ' | ' + str(level_name) + ' '

        for arg in args:                                # read in the list of values
            message += str(arg)                        # use str to convert any arg to a string
                                                        # add these to the message

        print(message,'<')                            # add this is the end to help you
                                                        # split the logs into seperate
                                                        # lines


############################################
# End of gyro drive functions
############################################

#################################################
# spinny Class
# Designed to drive 1 motor to spin to
# specific degrees as a certain speed
# Modify but do not remove
#################################################

class spinny:
    PROBLEM        = -1                                        # If a problem happens. Will also throw an exception.
    CODE_RESET    = 0                                        # this is reset at the beginning of the gyro_drive functions
    RUNNING        = 1
    TARGET_REACHED = 2                                        # robot achieved the desired target

    # used to hold the values when we go async.
    velocity = 0
    speed = 0
    target_deg = 0
    position = 0
    async_op = False

    # this is the class constructor                            # Google python class constructor
    def __init__(self,
        handle,                                                # give it a 4 character name
        port,                                                # what motor port, use port.enum
        max_deg,                                                # maximum degrees or motor travel
        max_vel,                                                # motor maximum velocity
        accuracy = 1,                                        # target envelope target +/- 1
        stop_mode = motor.SMART_BRAKE,                        # motor behavior on stop
        close_degrees = 60,                                    # how close do we shift to slow.
        close_speed = 10):                                    # speed close to target for accuracy

        self.handle = handle                                    # google python class self
        self.motor_port = port                                # we are passing the values
        self.max_degrees = max_deg                            # you put in here, into class
        self.max_velocity = max_vel                            # variables. They may have the
        self.accuracy = accuracy                                # name but the are different.
        self.close_speed = close_speed                        # self means they belong to the
        self.close_degrees = close_degrees                    # class
        self.stop_mode = stop_mode

        # internal fields.
        self.result_code = spinny.CODE_RESET
        self.reset()                                            # reset the motor relative start
                                                                # position. See reset definition
                                                                # below.

    def get_result(self):                                    # get the last result code.
        return self.result_code

    def reset(self):
        motor.reset_relative_position(self.motor_port,0)        # reset the motors relative position to 0

    def get_relative_pos(self):
        return motor.relative_position(self.motor_port)        # get the relative motor position
                                                                # notice it references the classes motor port.

    def get_motor_port(self):
        return self.motor_port                                # return the class motor port for other methods


    def spin_motor(self):

        while True:                                                # this loop moves the motor.
            direction = 0                                        # seed to stop if pass through tests



            our_relative_deg = \
                    motor.relative_position(self.motor_port)        # get where we are now

            self.target_dist = abs(our_relative_deg - self.target_deg)        # how close we are to the target?


            log( log_level.END ,self.handle,
            " | run ",
            " | position: ", self.position, "%",
            " | target deg: " , self.target_deg,
            " | target_distance ", self.target_dist,
            " | relative deg ", our_relative_deg)

            # target envelop - show on a horizontal number line    # we use abs here. Target envelope is 1,0,-1
            if self.target_dist <= self.accuracy: break                    # are we within 1 degree of the target?
            elif our_relative_deg <= self.target_deg: direction = 1    # are we below the target, we move up?
            elif our_relative_deg >= self.target_deg: direction = -1    # are we above the target, we move down?

            if self.target_dist < self.close_degrees and \
                                self.velocity != self.close_velocity:        # we are close, now use close_velocity
                self.velocity = self.close_velocity                        # we will use this until we hit envelope.

            motor.run(self.motor_port, int(self.velocity) * direction)# update the motors velocity.

            if self.async_op == True: return                            # bug out when using async

        motor.stop(self.motor_port, stop=self.stop_mode)                # when we stop we apply the stop_mode

        self.result_code = spinny.TARGET_REACHED
                                                                        # these are defined under motor
        log( log_level.END ,self.handle,
            " | run ",
            " | position: ", self.position, "%",
            " | target deg: " , self.target_deg)

    @staticmethod
    def spin_multi_motors(motor_list, async_op=False):
        total_spinnys_finished = 0
        total_spinnys = len(motor_list)                                # how many spinnys do I have
        if total_spinnys < 1:                                        # no spinnys were passed in the list
            return

        while total_spinnys_finished < total_spinnys :
            total_spinnys_finished = 0                                # reset here
            for spinny_instance in motor_list:                        # check each spinny in the list
                if spinny_instance.result_code == spinny.RUNNING:    # if we are running
                    spinny_instance.spin_motor()                        # keep spinning, we do not stay here
                else:
                    total_spinnys_finished += 1

            if async_op == True:                                        # in async mode we will be called
                return                                                # by an outside loop



    def run(self, position, speed=10,
        close_speed_override = None,                            # allows you to override the class versions
        close_degrees_override = None,
        stop_mode_override = None,
        accuracy_override = None,
        async_op = None):

        """
        spinny.run - Run the motor assigned to the spinny class
                    You can overide the class settings here.
                    These will not change the class settings.
                    You do that when you init it.
        """
        self.result_code = spinny.RUNNING

        #######################################################
        # use overrides without changing the class versions.
        # if overrides came in as not None,
        # then we want to use them once without
        # changing the class constructor settings.
        #######################################################
        if accuracy_override is not None:                    # user passed a value here so use it
            self.accuracy = accuracy_override
                                                                # self version. The self version is not changed
        if close_degrees_override is not None:
            self.close_degrees = close_degrees_override

        if close_speed_override is not None:
            self.close_speed = close_speed_override

        if stop_mode_override is not None:
            self.stop_mode = stop_mode_override

        self.async_op = async_op                                # the passed value has the same name.
                                                                # but they are different


        self.target_deg = calc_pct_value( self.max_degrees, position)        # convert position% to the target degrees

        #self.target_deg = position

        # Define the 2 veloocities
        self.velocity = calc_pct_value(self.max_velocity, speed)        # convert speed% to desired velocity

        self.close_velocity = \
                calc_pct_value(self.max_velocity, self.close_speed)    # as we get close to target slow down for accuracy

        log( log_level.START ,self.handle,
            " | run ", " | position: ", self.position, "%",
            " | speed: ", self.speed, " | target deg: " , self.target_deg,
            " | accuracy: ", self.accuracy )

        self.spin_motor()


###################################
# End spinny Class
###################################

main() # this is where main is called and the program runs.






