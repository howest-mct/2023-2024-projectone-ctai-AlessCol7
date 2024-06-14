import socket
import threading
import time
import csv
from datetime import datetime
from RPi import GPIO
from Classes.Buzzer import BuzzerController
from Classes.LCD import LCD
from Classes.RGBLEDController import RGBLEDController
from subprocess import check_output

# Global vars for use in methods/threads
client_socket = None
server_socket = None
server_thread = None
shutdown_flag = threading.Event()

# GPIO setup
BUZZER_PIN = 12
I2C_ADDR = 0x27
rgb_pins = (5, 6, 13)

def setup_socket_server():
    global server_socket, server_thread, shutdown_flag
    # Socket setup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket instance
    server_socket.bind(('0.0.0.0', 1443))  # Bind on all available IPs (WiFi and LAN), on port 1442
    server_socket.settimeout(0.2)  # Timeout for listening, needed for loop in thread, otherwise it's blocking
    server_socket.listen(1)  # Enable "listening" for requests/connections

    # Start the server thread
    server_thread = threading.Thread(target=accept_connections, args=(shutdown_flag,), daemon=True)
    server_thread.start()

def accept_connections(shutdown_flag):
    global client_socket
    print("Accepting connections")
    while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
        try:
            client_socket, addr = server_socket.accept()  # Accept incoming requests, and return a reference to the client and its IP
            print("Connected by", addr)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, shutdown_flag,))
            client_thread.start()
        except socket.timeout:  # Ignore timeout errors
            pass

def handle_client(sock, shutdown_flag):
    try:
        while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
            current_time = datetime.now().strftime('%a-%p').upper()
            day, part = current_time.split("-")
            current_time = f"{day}-{part.lower()}"

            sock.send(current_time.encode())  # Send current day and time to AI part
            data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
            if not data:  # When no data is received, try again (and shutdown flag is checked again)
                break
            message = data.decode()
            print("Received from client:", message)
            if message == "Wrong pill detected":
                activate_buzzer()
                red_light()
            elif message == "Right pill detected":
                green_light()
               
    except socket.timeout:  # Capture the timeouts
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def log_timestamp():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('buzzer_logs.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp])
    print(f"Logged timestamp: {timestamp}")

def activate_buzzer():
    try:
        buzzer.bad_notification()
        log_timestamp()
    except Exception as e:
        print(f"Failed to activate buzzer: {e}")

def red_light():
    try:
        rgb_led_controller.show_red()
        time.sleep(2)
        rgb_led_controller.turn_off()
    except Exception as e:
        print(f"Failed to turn on red light: {e}")

def green_light():
    try:
        rgb_led_controller.show_green()
        time.sleep(2)
        rgb_led_controller.turn_off()
    except Exception as e:
        print(f"Failed to turn on green light: {e}")


def getIp():
    ips = str(check_output(['hostname', '--all-ip-addresses']))
    ips = ips[2:len(ips)-4]
    ips = ips.split(" ")
    return ips

###### MAIN PART ######
try:
    # Class initialization
    buzzer = BuzzerController(pin=BUZZER_PIN)
    lcd = LCD(I2C_ADDR)
    rgb_led_controller = RGBLEDController(rgb_pins)

    # Get IP displaying
    ip = getIp()
    lcd.send_string(ip[0], 1)
    lcd.send_string(ip[1], 2)

    # Run socket server
    setup_socket_server()
    while True:
        time.sleep(10)

except KeyboardInterrupt:
    print("Server shutting down")
    shutdown_flag.set()  # Set the shutdown flag
finally:
    server_thread.join()  # Join the thread, so we wait for it to finish (graceful exit)
    if server_socket:
        server_socket.close()  # Make sure to close any open connections
    if buzzer:
        buzzer.cleanup()
    if lcd:
        lcd.cleanup()
    if rgb_led_controller:
        rgb_led_controller.cleanup()










