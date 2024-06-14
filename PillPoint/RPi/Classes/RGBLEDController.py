import smbus
from RPi import GPIO
import time

class RGBLEDController:
    def __init__(self, rgb_pins):
        self.rgb_pins = rgb_pins
        self.rgb_r, self.rgb_g, self.rgb_b = rgb_pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(rgb_pins, GPIO.OUT)
        self.rgb_r_pwm = GPIO.PWM(self.rgb_r, 500)
        self.rgb_r_pwm.start(100)
        self.rgb_b_pwm = GPIO.PWM(self.rgb_b, 500)
        self.rgb_b_pwm.start(100)
        self.rgb_g_pwm = GPIO.PWM(self.rgb_g, 500)
        self.rgb_g_pwm.start(100)

    def set_color(self, pwm_val_r, pwm_val_g, pwm_val_b):
        self.rgb_r_pwm.ChangeDutyCycle(100 - pwm_val_r)
        self.rgb_g_pwm.ChangeDutyCycle(100 - pwm_val_g)
        self.rgb_b_pwm.ChangeDutyCycle(100 - pwm_val_b)

    def cleanup(self):
        self.rgb_r_pwm.stop()
        self.rgb_g_pwm.stop()
        self.rgb_b_pwm.stop()
        GPIO.cleanup()

    def show_red(self):
        self.set_color(100, 0, 0)

    def show_green(self):
        self.set_color(0, 100, 0)

    def turn_off(self):
        self.set_color(0, 0, 0)

class ADCReader:
    def __init__(self, ADC_addr):
        self.i2c = smbus.SMBus(1)
        self.ADC_addr = ADC_addr
        self.command_for_chanel2 = 0b1001
        self.command_for_chanel3 = 0b1101
        self.command_for_chanel4 = 0b1111

    def read_analog_value(self):
        self.i2c.write_byte(self.ADC_addr, self.command_for_chanel2 << 4 | 0x4)
        self.i2c.write_byte(self.ADC_addr, self.command_for_chanel3 << 4 | 0x4)
        self.i2c.write_byte(self.ADC_addr, self.command_for_chanel4 << 4 | 0x4)
        analog_value = self.i2c.read_byte(self.ADC_addr)
        return analog_value

# if __name__ == "__main__":
#     try:
#         rgb_pins = (5, 6, 13)
#         rgb_led_controller = RGBLEDController(rgb_pins)
#         adc_reader = ADCReader(0x48)

#         while True:
#             analog_value = adc_reader.read_analog_value()
#             pwm_val_r = analog_value / 255.0 * 100
#             pwm_val_g = analog_value / 255.0 * 100
#             pwm_val_b = analog_value / 255.0 * 100
#             rgb_led_controller.set_color(pwm_val_r, pwm_val_g, pwm_val_b)
#             time.sleep(0.15)

#     except KeyboardInterrupt:
#         pass

#     finally:
#         rgb_led_controller.cleanup()

# Example usage
if __name__ == "__main__":
    rgb_led_controller = RGBLEDController(rgb_pins=[5, 6, 13])  # Replace with your actual GPIO pins
    try:
        rgb_led_controller.show_red()
        time.sleep(2)
        rgb_led_controller.show_green()
        time.sleep(2)
        rgb_led_controller.turn_off()
    finally:
        rgb_led_controller.cleanup()
