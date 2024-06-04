import socket
import threading
import time
from time import sleep
from RPi import GPIO
from Classes.Buzzer import BuzzerController
from Classes.LCD import LCD
from subprocess import check_output

# Global vars for use in methods/threads
client_socket = None
server_socket = None
server_thread = None
shutdown_flag = threading.Event()

# GPIO setup
BUZZER_PIN = 12
I2C_ADDR = 0x27

def setup_socket_server():
    global server_socket, server_thread, shutdown_flag
    # Socket setup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket instance
    server_socket.bind(('0.0.0.0', 1442))  # Bind on all available IPs (WiFi and LAN), on port 1441
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
            data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
            if not data:  # When no data is received, try again (and shutdown flag is checked again)
                break
            message = data.decode()
            print("Received from client:", message)
            if message == "Wrong pill detected":
                activate_buzzer()
    except socket.timeout:  # Capture the timeouts
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def activate_buzzer():
    try:
        buzzer.bad_notification()
    except Exception as e:
        print(f"Failed to activate buzzer: {e}")

def getIp():
    ips = str(check_output(['hostname', '--all-ip-addresses']))
    ips = ips[2:len(ips)-4]
    ips = ips.split(" ")
    return ips

###### MAIN PART ######
try:
    #class initialization
    buzzer = BuzzerController(pin=BUZZER_PIN)
    lcd = LCD(I2C_ADDR)

    #get ip displaying
    ip = getIp()
    #lcd.send_string('IP adress:', 1)
    lcd.send_string(ip[0],1)
    lcd.send_string(ip[1],2)
    #print(ip)

    #run socket server
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
    # GPIO.cleanup()
