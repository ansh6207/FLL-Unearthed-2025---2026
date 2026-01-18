import color_sensor
from hub import port
import color

if color_sensor.color(port.E) is color.RED:
    print("Red Detected")

elif color_sensor.color(port.E) is color.ORANGE:
    print("Orange Detected")

elif color_sensor.color(port.E) is color.YELLOW:
    print("Yellow Detected")

elif color_sensor.color(port.E) is color.GREEN:
    print("Green Detected")

elif color_sensor.color(port.E) is color.BLUE:
    print("Blue Detected")

elif color_sensor.color(port.E) is color.PURPLE:
    print("Purple Detected")

elif color_sensor.color(port.E) is color.BLACK:
    print("Black Detected")

elif color_sensor.color(port.E) is color.AZURE:
    print("Azure Detected")

elif color_sensor.color(port.E) is color.MAGENTA:
    print("Magenta Detected")

elif color_sensor.color(port.E) is color.TURQUOISE:
    print("Turquoise Detected")

elif color_sensor.color(port.E) is color.WHITE:
    print("White Detected")

elif color_sensor.color(port.E) is color.UNKNOWN:
    print("Unknown Color Detected")

else:
    pass
