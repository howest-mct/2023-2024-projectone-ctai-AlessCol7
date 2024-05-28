import cv2
import time
import queue
import threading
from Buzzer import BuzzerController
from AI.app import detect_objects, is_pill_taken, log_pill_taken_event
from bluetooth_uart_server.bluetooth_uart_server import ble_gatt_uart_loop

def ble_gatt_uart_loop(rx_q, tx_q, device_name):
    # BLE GATT UART loop code here
    i = 0
    rx_q = queue.Queue()
    tx_q = queue.Queue()
    device_name = "AlessCol-pi-gatt-uart" # replace with your own (unique) device name
    threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()
    while True:
        try:
            incoming = rx_q.get(timeout=1) # Wait for up to 1 second 
            if incoming:
                print("In main loop: {}".format(incoming))
        except Exception as e:
            pass # nothing in Q 
    

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

if __name__ == '__main__':
    i = 0
    rx_q = queue.Queue()
    tx_q = queue.Queue()
    device_name = "AlessCol-pi-gatt-uart"
    threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()
    main()