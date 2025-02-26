import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import cv2  # OpenCV library for computer vision tasks
from ultralytics import YOLO  # YOLO model for object detection
from PIL import Image, ImageTk  # PIL for image processing and integration with Tkinter
import tkinter as tk  # Tkinter for GUI
import socket  # Socket for network communication
import threading  # Threading for concurrent operations
import time  # Time for handling time-related operations
import logging  # For logging configurations
import sys  # For redirecting standard output
import os  # For setting environment variables
import contextlib  # For suppressing print statements



# Suppress logging from specific libraries
logging.getLogger('ultralytics').setLevel(logging.ERROR)
logging.getLogger('torch').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

# Suppress OpenCV debug prints using environment variable
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'

# Context manager to suppress print statements
@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# Load the trained YOLOv8 model
try:
    with suppress_stdout():
        model = YOLO('PillPoint/AI/PillPoint.v6i.yolov8/runs/detect/train3/weights/best.pt')
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Define the class names
class_names = ['FRI-am', 'FRI-pm', 'Hands', 'MON-am', 'MON-pm', 'Open', 'Pill', 'PillBox', 'SAT-am', 'SAT-pm', 'SUN-am', 'SUN-pm', 'THU-am', 'THU-pm', 'TUE-am', 'TUE-pm', 'WED-am', 'WED-pm']

# Define the day and time slots for the pillbox compartments
day_time_slots = ['MON-am', 'MON-pm', 'TUE-am', 'TUE-pm', 'WED-am', 'WED-pm', 'THU-am', 'THU-pm', 'FRI-am', 'FRI-pm', 'SAT-am', 'SAT-pm', 'SUN-am', 'SUN-pm']

# Define colors for each class visualization
class_colors = {
    'FRI-am': (0, 255, 255),
    'FRI-pm': (255, 255, 0),
    'Hands': (0, 255, 0),
    'MON-am': (255, 0, 255),
    'MON-pm': (0, 255, 255),
    'Open': (255, 255, 0),
    'Pill': (255, 0, 0),
    'PillBox': (0, 255, 255),
    'SAT-am': (255, 165, 0),
    'SAT-pm': (255, 69, 0),
    'SUN-am': (128, 0, 128),
    'SUN-pm': (75, 0, 130),
    'THU-am': (0, 255, 255),
    'THU-pm': (0, 128, 128),
    'TUE-am': (255, 0, 255),
    'TUE-pm': (128, 0, 0),
    'WED-am': (0, 0, 255),
    'WED-pm': (0, 128, 0)
}

label_centre_points_dict = {}
label_cord_box = {'WED-pm': [943, 1060, 675, 869],
                  'WED-am': [945, 1057, 469, 661],
                  'THU-am': [837, 950, 472, 658],
                  'FRI-am': [710, 835, 466, 654], 
                  'SAT-am': [600, 708, 461, 667], 
                'THU-pm': [830, 940, 681, 869],   
                'Mon-am': [1182, 1297, 466, 654], 
                'FRI-pm': [712, 819, 674, 872], 
                 'SAT-pm': [600, 708, 691, 867],
                'TUE-pm': [1066, 1175, 675, 869], 
                'TUE-am': [1065, 1171, 472, 659], 
                'SUN-pm': [1312, 1409, 688, 870], 
                'MON-pm': [1191, 1305, 671, 865],
                'SUN-am': [1312, 1415, 465, 655]}

# Server address and port for Raspberry Pi
server_address = ('192.168.168.167', 1443)  # Change this to your Raspberry Pi IP and port

# Global vars for use in methods/threads
client_socket = None
receive_thread = None
shutdown_flag = threading.Event()
last_debug_time = time.time()
debug_interval = 2
current_day_time = None

def setup_socket_client():
    global client_socket, receive_thread
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket instance
    client_socket.connect(server_address)  # Connect to specified server
    print("Connected to server")

    # Start a thread to handle incoming messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, shutdown_flag))
    receive_thread.start()

def receive_messages(sock, shutdown_flag):
    global current_day_time
    sock.settimeout(1)  # Set a timeout on the socket so we can check shutdown_flag.is_set in the loop, instead of blocking
    try:
        while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
            try:
                data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
                if not data:  # When no data is received, try again (and shutdown flag is checked again)
                    break
                current_day_time = data.decode()
                print("Received from server:", current_day_time)  # Print the received data, or do something with it
            except socket.timeout:  # When no data comes within timeout, try again
                continue
    except Exception as e:
        if not shutdown_flag.is_set():
            print(f"Connection error: {e}")
    finally:
        sock.close()

def request_date_time():
    global client_socket
    try:
        client_socket.sendall("Request date and time".encode())
    except Exception as e:
        print(f"Failed to request date and time: {e}")

# Function to draw bounding boxes with different colors
import datetime
sc_timer = datetime.timedelta(seconds=6)
current_time = datetime.datetime.now()
previous_time = current_time
took_sc = False
def draw_bounding_boxes(image, results):
    global last_debug_time, current_day_time, current_time, previous_time, sc_timer, took_sc
    current_time = datetime.datetime.now()
    boxes = results[0].boxes.xyxy.cpu().numpy()
    confs = results[0].boxes.conf.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()
    
    pillbox_detected = False
    compartment_open_detected = False
    wrong_compartment_opened = False
    detected_labels = []  # Initialize an empty list to store detected labels
    open_label_centred = None
    # if current_time - previous_time > sc_timer and took_sc == False:
    #     took_sc = True
    #     print('TOOK BOXES SC')
    #     for i, box in enumerate(boxes):
    #         x1, y1, x2, y2 = map(int, box)
    #         conf = confs[i]
    #         cls = int(classes[i])
    #         label = class_names[cls]
    #         if label in day_time_slots:
    #             label_cord_box[label] = [x1, x2, y1, y2]
        
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        conf = confs[i]
        cls = int(classes[i])
        label = class_names[cls]
        if label in day_time_slots:
            detected_labels.append(label)  # Append the detected label to the list

        # Store the center coordinates of the detected label's bounding box
            label_centre_points_dict[label] = [(x1 + x2) / 2, (y1 + y2) / 2]
    
        color = class_colors.get(label, (0, 0, 255))  # Default to blue if not found
        
        
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, f'{label} {confs[i]:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        # asking the coordinates of the bounding boxes        
        # when it opens it I check the coordinates
        # a list with all the coordinates on top of them


        if label == 'PillBox':
            pillbox_detected = True


        if label == 'Open':
            compartment_open_detected = True
            open_label_centred =  [(x1+x2)/2,(y1+y2)/2]
            for key, value in label_cord_box.items():
                if open_label_centred[0] > value[0] and open_label_centred[0] < value[1] and open_label_centred[1] > value[2] and open_label_centred[1] < value[3]:
                    label_open = key
                    if label_open != current_day_time:
                        wrong_compartment_opened = True
    
        if (compartment_open_detected == True and wrong_compartment_opened == True):
            send_buzzer_notification()
        elif (compartment_open_detected == True and wrong_compartment_opened == False):
            send_green_notification()
    
    # for key, value in label_cord_box.items():
    #     cv2.rectangle(image, (value[0], value[2]), (value[1], value[3]), (255, 0, 0), 2)
    #     cv2.putText(image, f'{key}', (value[0], value[2] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)


    # Check if it's time to print debug statements
    if last_debug_time + debug_interval < time.time():
        # Debug statements to verify logic
        print(f"Current Day and Time: {current_day_time}")
        print(f"Pillbox Detected: {pillbox_detected}")
        print(f"Compartment Open Detected: {compartment_open_detected}")
        print(f"Wrong Compartment Opened: {wrong_compartment_opened}")
        print(f"Detected Labels: {detected_labels}")
        print(f"Centre of open: {open_label_centred}")
        print(f'labels sc : {label_cord_box}')
        # Update the last debug time
        last_debug_time = time.time()

def send_buzzer_notification():
    global client_socket
    try:
        client_socket.sendall("Wrong pill detected".encode())
    except Exception as e:
        print(f"Failed to send buzzer notification: {e}")

def send_green_notification():
    global client_socket
    try:
        client_socket.sendall("Right pill detected".encode())
    except Exception as e:
        print(f"Failed to send RGB notification: {e}")

# AI part
def process_frame(frame):
    # Perform inference with the YOLOv8 model
    try:
        with suppress_stdout():
            results = model(frame)
    except Exception as e:
        print(f"Error performing inference: {e}")
        return frame

    # Annotate the frame with detection results
    draw_bounding_boxes(frame, results)

    return frame

# Tkinter GUI part
def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert colorspace from BGR to RGB
        frame = process_frame(frame)  # Calls process_frame(frame) to perform object detection and annotation on the frame.
        img = Image.fromarray(frame)  # Converts the processed frame (which is a numpy array) to a PIL Image object using Image.fromarray.
        imgtk = ImageTk.PhotoImage(image=img)  # Converts the PIL Image to a format suitable for displaying in a Tkinter GUI using ImageTk.PhotoImage.
        label_img.imgtk = imgtk  # Updates the image displayed in the Tkinter Label widget (label_img) with the new frame by setting its image attribute to imgtk.
        label_img.configure(image=imgtk)
    else:
        print("Error reading frame from webcam")
    label_img.after(10, update_frame)  # Schedule the update after 10 milliseconds

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Setup Tkinter window
window = tk.Tk()
window.title("Pill Detection")
window.geometry("800x600")

# Create a label to display the webcam feed
label_img = tk.Label(window)
label_img.pack()

# Start the socket client
setup_socket_client()

# Request the initial date and time
request_date_time()

# Start the webcam feed update
update_frame()

# Start the Tkinter event loop
window.mainloop()

# Release the webcam
cap.release()
