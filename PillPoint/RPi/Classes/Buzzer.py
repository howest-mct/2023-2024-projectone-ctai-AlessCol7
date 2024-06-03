from RPi import GPIO
from time import sleep

class BuzzerController:
    def __init__(self, pin, frequency=200):
        self.pin = pin
        self.frequency = frequency
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.buzzer_pwm = GPIO.PWM(self.pin, self.frequency)

    def start(self, duty_cycle=50):
        self.buzzer_pwm.start(duty_cycle)

    def change_frequency(self, frequency):
        self.buzzer_pwm.ChangeFrequency(frequency)

    def stop(self):
        self.buzzer_pwm.stop()

    def cleanup(self):
        GPIO.cleanup(self.pin)
