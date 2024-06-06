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
        self.stop()
        GPIO.cleanup(self.pin)

    # def bad_notification(self):
    #     for freq in (500,400,500):
    #         self.start()
    #         self.change_frequency(freq)
    #         print(f'playing {freq}')
    #         sleep(0.8)
    #     self.stop()
    def bad_notification(self):
        print("Bad notification initiated")
        # Define a sequence of musical notes
        notes = [
            (440, 0.5),  # A4
            (493, 0.5),  # B4
            (523, 0.5),  # C5
            (587, 0.5),  # D5
            (659, 0.5),  # E5
            (698, 0.5),  # F5
            (784, 0.5)   # G5
            # (523, 0.2),  # C5
            # (466, 0.2),  # Bb4
            # (392, 0.3),  # G4
            # (349, 0.3)   # F4
        ]
        for freq, duration in notes:
            self.start()
            self.change_frequency(freq)
            print(f'playing {freq}')
            sleep(duration)
        self.stop()
        print("Bad notification completed")

# if __name__ == "__main__":
#     buzzer = BuzzerController(pin=12)
#     try:
#         buzzer.bad_notification()

#     finally:
#         buzzer.cleanup()


