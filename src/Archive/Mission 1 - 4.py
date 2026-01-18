from hub import port
import runloop
import motor_pair
import motor
from time import sleep, sleep_ms
import color_sensor
import color

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.E)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 2500,0, velocity=-600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 830,0, velocity=600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 600,0, velocity=-500)
    await motor.run_for_degrees(port.E, -400, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 600,0, velocity=-500)
    await motor.run_for_degrees(port.D, 275, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 700,0, velocity=500)
    await motor.run_for_degrees(port.D, -275, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 1000,0, velocity=-300)
    await motor.run_for_degrees(port.E, -200, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 850,0, velocity=500)
    await motor.run_for_degrees(port.C, -240, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 700,0, velocity=500)
    await motor.run_for_degrees(port.C, 70, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 1000,0, velocity=-500)
runloop.run(main())
