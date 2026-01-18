from hub import port
import runloop
import motor_pair
import motor
from time import sleep, sleep_ms
import color_sensor
import color

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.E)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 3200,0, velocity=240)
    await motor.run_for_degrees(port.D, -200, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1,500,0, velocity=-220)
    await motor_pair.move_for_time(motor_pair.PAIR_1,1450,0, velocity=240)
    await motor.run_for_degrees(port.D, 200, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1,100,0, velocity=-220)
    await motor.run_for_degrees(port.A, 200, 600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 800,0, velocity=240)
    await motor.run_for_degrees(port.A, 200, -430)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 1500,0, velocity=100)
    if color_sensor.color(port.F) is color.BLACK or color.WHITE:
        print("detected after mission 12")
        motor_pair.stop
    await motor.run_for_degrees(port.A, 200, 550)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 2500,0, velocity=100)
    await motor.run_for_degrees(port.A, 200, 550)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 1400,0, velocity=200)
    await motor.run_for_degrees(port.D, 200, -600)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 2000,0, velocity=100)
    await motor.run_for_degrees(port.D, 200, 600)
    await motor.run_for_degrees(port.A, 200, -550)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 2500,0, velocity=100)
    await motor.run_for_degrees(port.A, 200, -430)
    await motor_pair.move_for_time(motor_pair.PAIR_1, 2000,0, velocity=300)
runloop.run(main())
