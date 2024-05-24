from lgpio import rpi-lgpio
from time import sleep

class BuzzerController:
    def __init__(self, pin=4, frequency=200):
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
        GPIO.cleanup()

if __name__ == "__main__":
    buzzer = BuzzerController()
    try:
        buzzer.start()
        for freq in range(300, 800, 100):
            buzzer.change_frequency(freq)
            sleep(1)
    finally:
        buzzer.stop()
