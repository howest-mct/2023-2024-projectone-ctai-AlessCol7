# import socket
# import threading
# import time
# from time import sleep
# from RPi import GPIO
# from Classes.Buzzer import BuzzerController
# from Classes.LCD import LCD
# from subprocess import check_output

# # Global vars for use in methods/threads
# client_socket = None
# server_socket = None
# server_thread = None
# shutdown_flag = threading.Event()

# # GPIO setup
# BUZZER_PIN = 12
# I2C_ADDR = 0x27

# def setup_socket_server():
#     global server_socket, server_thread, shutdown_flag
#     # Socket setup
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket instance
#     server_socket.bind(('0.0.0.0', 1442))  # Bind on all available IPs (WiFi and LAN), on port 1441
#     server_socket.settimeout(0.2)  # Timeout for listening, needed for loop in thread, otherwise it's blocking
#     server_socket.listen(1)  # Enable "listening" for requests/connections

#     # Start the server thread
#     server_thread = threading.Thread(target=accept_connections, args=(shutdown_flag,), daemon=True)
#     server_thread.start()

# def accept_connections(shutdown_flag):
#     global client_socket
#     print("Accepting connections")
#     while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
#         try:
#             client_socket, addr = server_socket.accept()  # Accept incoming requests, and return a reference to the client and its IP
#             print("Connected by", addr)
#             client_thread = threading.Thread(target=handle_client, args=(client_socket, shutdown_flag,))
#             client_thread.start()
#         except socket.timeout:  # Ignore timeout errors
#             pass

# def handle_client(sock, shutdown_flag):
#     try:
#         while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
#             data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
#             if not data:  # When no data is received, try again (and shutdown flag is checked again)
#                 break
#             message = data.decode()
#             print("Received from client:", message)
#             # if message == "Wrong compartment opened":
#             #     activate_buzzer()
#             if "Wrong compartment opened" in message:
#                 print("Activating buzzer")
#                 activate_buzzer()
#     except socket.timeout:  # Capture the timeouts
#         pass
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         sock.close()
        

# # def activate_buzzer():
# #     try:
# #         buzzer.bad_notification()
# #     except Exception as e:
# #         print(f"Failed to activate buzzer: {e}")
# def activate_buzzer():
#     try:
#         print("Buzzer activation initiated.")
#         buzzer.bad_notification()
#         print("Buzzer activation completed.")
#     except Exception as e:
#         print(f"Failed to activate buzzer: {e}")

# def getIp():
#     ips = str(check_output(['hostname', '--all-ip-addresses']))
#     ips = ips[2:len(ips)-4]
#     ips = ips.split(" ")
#     return ips

# ###### MAIN PART ######
# # try:
# #     #class initialization
# #     buzzer = BuzzerController(pin=BUZZER_PIN)
# #     lcd = LCD(I2C_ADDR)

# #     #get ip displaying
# #     ip = getIp()
# #     #lcd.send_string('IP adress:', 1)
# #     lcd.send_string(ip[0],1)
# #     lcd.send_string(ip[1],2)
# #     #print(ip)

# #     #run socket server
# #     setup_socket_server()
# #     while True:
# #         time.sleep(10)
# try:
#     #class initialization
#     buzzer = BuzzerController(pin=BUZZER_PIN)
#     lcd = LCD(I2C_ADDR)

#     #get ip displaying
#     ip = getIp()
#     lcd.send_string(ip[0], 1)
#     if len(ip) > 1:
#         lcd.send_string(ip[1], 2)

#     #run socket server
#     setup_socket_server()
#     while True:
#         time.sleep(10)

# except KeyboardInterrupt:
#     print("Server shutting down")
#     shutdown_flag.set()  # Set the shutdown flag
# finally:
#     server_thread.join()  # Join the thread, so we wait for it to finish (graceful exit)
#     if server_socket:
#         server_socket.close()  # Make sure to close any open connections
#     if buzzer:
#         buzzer.cleanup()
#     if lcd:
#         lcd.cleanup()
#     GPIO.cleanup()

# # import socket
# # import threading
# # import time
# # from datetime import datetime
# # from RPi import GPIO
# # from Classes.Buzzer import BuzzerController
# # from Classes.LCD import LCD
# # from subprocess import check_output
# # import csv

# # # Global variable for the CSV file name
# # CSV_FILE_NAME = "PillPoint.csv"

# # # Global vars for use in methods/threads
# # client_socket = None
# # server_socket = None
# # server_thread = None
# # shutdown_flag = threading.Event()

# # # GPIO setup
# # BUZZER_PIN = 12
# # I2C_ADDR = 0x27

# # def setup_socket_server():
# #     global server_socket, server_thread, shutdown_flag
# #     # Socket setup
# #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket instance
# #     server_socket.bind(('0.0.0.0', 1443))  # Bind on all available IPs (WiFi and LAN), on port 1441
# #     server_socket.settimeout(0.2)  # Timeout for listening, needed for loop in thread, otherwise it's blocking
# #     server_socket.listen(1)  # Enable "listening" for requests/connections

# #     # Start the server thread
# #     server_thread = threading.Thread(target=accept_connections, args=(shutdown_flag,), daemon=True)
# #     server_thread.start()

# # def accept_connections(shutdown_flag):
# #     global client_socket
# #     print("Accepting connections")
# #     while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
# #         try:
# #             client_socket, addr = server_socket.accept()  # Accept incoming requests, and return a reference to the client and its IP
# #             print("Connected by", addr)
# #             client_thread = threading.Thread(target=handle_client, args=(client_socket, shutdown_flag,))
# #             client_thread.start()
# #         except socket.timeout:  # Ignore timeout errors
# #             pass

# # def handle_client(sock, shutdown_flag):
# #     try:
# #         while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
# #             data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
# #             if not data:  # When no data is received, try again (and shutdown flag is checked again)
# #                 break
# #             message = data.decode()
# #             print("Received from client:", message)
# #             if "Compartiment opened" in message:
# #                 day, part_of_day = get_current_day_time()
# #                 compartiment = message.split(": ")[1]  # Extract compartiment from message
# #                 check_compartiment(day, part_of_day, compartiment)
# #     except socket.timeout:  # Capture the timeouts
# #         pass
# #     except Exception as e:
# #         print(f"Error: {e}")
# #     finally:
# #         sock.close()

# # def get_current_day_time():
# #     now = datetime.now()
# #     day = now.strftime("%a").upper()  # Get current day (e.g., MON, TUE, etc.)
# #     hour = now.strftime("%I")  # Get current hour (12-hour format)
# #     part_of_day = "AM" if now.strftime("%p") == "AM" else "PM"  # Check if it's AM or PM
# #     return day, part_of_day

# # def check_compartiment(day, part_of_day, compartiment):
# #     # Define the expected schedule for each compartiment
# #     expected_schedule = {
# #         "MON-AM": ["MON-AM", "TUE-AM", "WED-AM", "THU-AM", "FRI-AM", "SAT-AM", "SUN-AM"],
# #         "MON-PM": ["MON-PM", "TUE-PM", "WED-PM", "THU-PM", "FRI-PM", "SAT-PM", "SUN-PM"],
# #         # Add schedules for other days and times as needed
# #     }

# #     print("Current Day:", day)
# #     print("Part of Day:", part_of_day)
# #     print("Compartiment:", compartiment)

# #     if compartiment not in expected_schedule[day + "-" + part_of_day]:
# #         print("Wrong compartment opened!")
# #         write_to_csv(day, part_of_day, compartiment)
# #         activate_buzzer()
# #     else:
# #         print("Correct compartment opened.")

# # def write_to_csv(day, part_of_day, compartiment):
# #     with open(CSV_FILE_NAME, mode='a') as file:
# #         writer = csv.writer(file)
# #         writer.writerow([day, part_of_day, compartiment, datetime.now()])

# # def activate_buzzer():
# #     try:
# #         buzzer.bad_notification()
# #     except Exception as e:
# #         print(f"Failed to activate buzzer: {e}")

# # def getIp():
# #     ips = str(check_output(['hostname', '--all-ip-addresses']))
# #     ips = ips[2:len(ips)-4]
# #     ips = ips.split(" ")
# #     return ips

# # ###### MAIN PART ######
# # try:
# #     #class initialization
# #     buzzer = BuzzerController(pin=BUZZER_PIN)
# #     lcd = LCD(I2C_ADDR)

# #     #get ip displaying
# #     ip = getIp()
# #     lcd.send_string(ip[0], 1)
# #     if len(ip) > 1:
# #         lcd.send_string(ip[1], 2)

# #     # Create or clear the CSV file
# #     with open(CSV_FILE_NAME, mode='w') as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["Day", "Part of Day", "Compartiment", "Timestamp"])

# #     # Run socket server
# #     setup_socket_server()
# #     while True:
# #         time.sleep(10)

# # except KeyboardInterrupt:
# #     print("Server shutting down")
# #     shutdown_flag.set()  # Set the shutdown flag
# # finally:
# #     if server_thread:
# #         server_thread.join()  # Join the thread, so we wait for it to finish (graceful exit)
# #     if server_socket:
# #         server_socket.close()  # Make sure to close any open connections
# #     if buzzer:
# #         buzzer.cleanup()
# #     if lcd:
# #         lcd.cleanup()
# #     GPIO.cleanup()

# import socket
# import threading
# import time
# import csv
# from datetime import datetime
# from RPi import GPIO
# from Classes.Buzzer import BuzzerController
# from Classes.LCD import LCD
# from subprocess import check_output

# # Global vars for use in methods/threads
# client_socket = None
# server_socket = None
# server_thread = None
# shutdown_flag = threading.Event()

# # GPIO setup
# BUZZER_PIN = 12
# I2C_ADDR = 0x27

# def setup_socket_server():
#     global server_socket, server_thread, shutdown_flag
#     # Socket setup
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket instance
#     server_socket.bind(('0.0.0.0', 1442))  # Bind on all available IPs (WiFi and LAN), on port 1441
#     server_socket.settimeout(0.2)  # Timeout for listening, needed for loop in thread, otherwise it's blocking
#     server_socket.listen(1)  # Enable "listening" for requests/connections

#     # Start the server thread
#     server_thread = threading.Thread(target=accept_connections, args=(shutdown_flag,), daemon=True)
#     server_thread.start()

# def accept_connections(shutdown_flag):
#     global client_socket
#     print("Accepting connections")
#     while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
#         try:
#             client_socket, addr = server_socket.accept()  # Accept incoming requests, and return a reference to the client and its IP
#             print("Connected by", addr)
#             client_thread = threading.Thread(target=handle_client, args=(client_socket, shutdown_flag,))
#             client_thread.start()
#         except socket.timeout:  # Ignore timeout errors
#             pass

# # def handle_client(sock, shutdown_flag):
# #     try:
# #         while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
# #             data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
# #             if not data:  # When no data is received, try again (and shutdown flag is checked again)
# #                 break
# #             message = data.decode()
# #             print("Received from client:", message)
# #             if message == "Wrong pill detected":
# #                 activate_buzzer()
# #             elif message == "Request date and time":
# #                 send_date_time(sock)
# #     except socket.timeout:  # Capture the timeouts
# #         pass
# #     except Exception as e:
# #         print(f"Error: {e}")
# #     finally:
# #         sock.close()
# def handle_client(sock, shutdown_flag):
#     try:
#         while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
#             current_time = datetime.now().strftime('%a-%p')
#             sock.send(current_time.encode())  # Send current day and time to AI part
#             data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
#             if not data:  # When no data is received, try again (and shutdown flag is checked again)
#                 break
#             message = data.decode()
#             print("Received from client:", message)
#             if message == "Wrong pill detected":
#                 activate_buzzer()
#     except socket.timeout:  # Capture the timeouts
#         pass
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         sock.close()


# def log_timestamp():
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     with open('buzzer_logs.csv', mode='a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([timestamp])
#     print(f"Logged timestamp: {timestamp}")

# def activate_buzzer():
#     try:
#         buzzer.bad_notification()
#         log_timestamp()
#     except Exception as e:
#         print(f"Failed to activate buzzer: {e}")

# # def send_date_time(sock):
# #     try:
# #         current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# #         sock.sendall(current_time.encode())
# #     except Exception as e:
# #         print(f"Failed to send date and time: {e}")

# def getIp():
#     ips = str(check_output(['hostname', '--all-ip-addresses']))
#     ips = ips[2:len(ips)-4]
#     ips = ips.split(" ")
#     return ips

# ###### MAIN PART ######
# try:
#     #class initialization
#     buzzer = BuzzerController(pin=BUZZER_PIN)
#     lcd = LCD(I2C_ADDR)

#     #get ip displaying
#     ip = getIp()
#     #lcd.send_string('IP adress:', 1)
#     lcd.send_string(ip[0],1)
#     lcd.send_string(ip[1],2)
#     #print(ip)

#     #run socket server
#     setup_socket_server()
#     while True:
#         time.sleep(10)

# except KeyboardInterrupt:
#     print("Server shutting down")
#     shutdown_flag.set()  # Set the shutdown flag
# finally:
#     server_thread.join()  # Join the thread, so we wait for it to finish (graceful exit)
#     if server_socket:
#         server_socket.close()  # Make sure to close any open connections
#     if buzzer:
#         buzzer.cleanup()
#     if lcd:
#         lcd.cleanup()




import socket
import threading
import time
import csv
from datetime import datetime
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
            current_time = datetime.now().strftime('%a-%p')
            sock.send(current_time.encode())  # Send current day and time to AI part
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








