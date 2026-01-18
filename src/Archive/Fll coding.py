from hub import port
import runloop
import motor_pair
import motor
from time import sleep, sleep_ms

async def main():
    #motor_pair.pair(motor_pair.PAIR_1, port.A, port.E)
    #await motor_pair.move_for_time(motor_pair.PAIR_1,1000,0, velocity=240)
    #await motor.run_for_degrees(port.A, 150, 430)
    #await motor_pair.move_for_time(motor_pair.PAIR_1,3000,0, velocity=240)
    #await motor_pair.move_for_time(motor_pair.PAIR_1,1000,0, velocity=-240)
    #await motor.run_for_degrees(port.A, 140, 430)
    #await motor_pair.move_for_time(motor_pair.PAIR_1,2000,0, velocity=240)
    #await motor.run_for_degrees(port.A, -220, 430)
    #await motor_pair.move_for_time(motor_pair.PAIR_1,1000,0, velocity=240)
    #await motor.run_for_degrees(port.A, 95, 430)
    #await motor_pair.move_for_time(motor_pair.PAIR_1,3000,0, velocity=240)
    
runloop.run(main())
