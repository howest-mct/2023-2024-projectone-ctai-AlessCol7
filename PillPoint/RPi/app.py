# RPi/app.py

import cv2
import time
from Buzzer import BuzzerController
from AI.app import detect_objects, is_pill_taken, log_pill_taken_event

def capture_image():
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    if ret:
        image_path = '/home/pi/images/pill_image.jpg'
        cv2.imwrite(image_path, frame)
        vid.release()
        return image_path
    else:
        vid.release()
        raise RuntimeError("Failed to capture image")

def main():
    buzzer = BuzzerController()
    while True:
        try:
            image_path = capture_image()
            pills, pillboxes, hands = detect_objects(image_path)
            
            if is_pill_taken(pills, pillboxes, hands):
                buzzer.start()  # Sound the buzzer
                time.sleep(1)  # Buzzer duration
                buzzer.stop()
                log_pill_taken_event()
            
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Wait a minute before trying again

if __name__ == "__main__":
    main()
