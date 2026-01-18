from hub import port
import runloop
import motor_pair
import motor
from time import sleep, sleep_ms

async def main():
    await motor.run_for_degrees(port.C, -2600, 1000)
runloop.run(main())
