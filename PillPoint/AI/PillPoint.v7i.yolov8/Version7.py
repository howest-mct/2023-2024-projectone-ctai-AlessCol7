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
        model = YOLO('/Users/alessiacolumban/Desktop/2023-2024-projectone-ctai-AlessCol7/PillPoint/AI/PillPoint.v7i.yolov8/runs/detect/train/weights/best.pt')
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

# Server address and port for Raspberry Pi
server_address = ('192.168.168.167', 1443)  # Change this to your Raspberry Pi IP and port

# Global vars for use in methods/threads
client_socket = None
receive_thread = None
shutdown_flag = threading.Event()
last_debug_time = time.time()
debug_interval = 2
current_day_time = None
detected_labels_and_locations_stack = []

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

def group_results(results):
    def __get_distance(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    
    boxes = results[0].boxes.xyxy.cpu().numpy()
    confs = results[0].boxes.conf.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()
    zips = [(box, conf, class_name) for box, conf, class_name in zip(boxes, confs, classes) if conf > 0.5]
    detected_labels_and_locations = []  # Initialize an empty list to store detected labels and their locations (label, center_x, center_y, (width, height))
    threshold = 200

    for i, result in enumerate(zips):
        x1, y1, x2, y2 = map(int, result[0])
        conf = result[1]
        cls = int(result[2])
        label = class_names[cls]
        if label in day_time_slots:
            detected_labels_and_locations.append((label, (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1, conf))  # Append the label and its location to the list

    current_smooth = []
    for group in detected_labels_and_locations_stack:
        average_x = sum(x for _, x, _, _, _, _ in group) / len(group)
        average_y = sum(y for _, _, y, _, _, _ in group) / len(group)
        current_smooth.append((average_x, average_y))

    for label, x, y, width, height, conf in detected_labels_and_locations:
        closest = None
        closest_index = None
        for i, (x2, y2) in enumerate(current_smooth):
            current_distance = __get_distance((x, y), (x2, y2))
            if closest is None or current_distance < closest:
                closest = current_distance
                closest_index = i
        result = (label, x, y, width, height, conf)
        if closest is not None and closest < threshold:
            detected_labels_and_locations_stack[closest_index].append(result)
            current_smooth.pop(closest_index)
        else:
            detected_labels_and_locations_stack.append([result])

    for group in detected_labels_and_locations_stack:
        # remove worst result by confidence or result contradicting most results
        if len(group) > 30:
            group.pop(0)

# Function to draw bounding boxes with different colors
def draw_bounding_boxes(image, results):
    global last_debug_time, current_day_time
    group_results(results)
    pillbox_detected = False
    compartment_open_detected = False
    wrong_compartment_opened = False
    detected_labels = []

    smoothed_results = []
    for group in detected_labels_and_locations_stack:
        labels = set(label for label, _, _, _, _, _ in group)
        confidence = {}
        for label in labels:
            this_labels = [(l, conf) for l, _, _, _, _, conf in group if label == l]
            confidence[label] = sum([conf for _, conf in this_labels]) / len(this_labels)

        best_label = max(confidence.items(), key=lambda x: x[1])
        average_x = sum(x for _, x, _, _, _, _ in group) / len(group)
        average_y = sum(y for _, _, y, _, _, _ in group) / len(group)
        average_width = sum(width for _, _, _, width, _, _ in group) / len(group)
        average_height = sum(height for _, _, _, _, height, _ in group) / len(group)
        smoothed_results.append((best_label[0], best_label[1], average_x - average_width / 2, average_y - average_height / 2, average_x + average_width / 2, average_y + average_height / 2))

    duplicates = []
    for label in set(label for label, _, _, _, _, _ in smoothed_results):
        label_group = [(i, result) for i, result in enumerate(smoothed_results) if result[0] == label]

        best = max(label_group, key=lambda x: x[1][1])
        duplicates += [i for i, result in label_group if result[1] < best[1][1]]
    
    for duplicate_id in duplicates:
        smoothed_results[duplicate_id] = None

    smoothed_results = [result for result in smoothed_results if result]    

    for label, _, x1, y1, x2, y2 in smoothed_results:
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        color = class_colors.get(label, (0, 0, 255))  # Default to blue if not found
        
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, f'{label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        if label == 'PillBox':
            pillbox_detected = True

        if label == 'Open':
            compartment_open_detected = True
            
    # Check if it's time to print debug statements
    if last_debug_time + debug_interval < time.time():
        # Debug statements to verify logic
        print(f"Current Day and Time: {current_day_time}")
        print(f"Pillbox Detected: {pillbox_detected}")
        print(f"Compartment Open Detected: {compartment_open_detected}")
        print(f"Wrong Compartment Opened: {wrong_compartment_opened}")
        print(f"Detected Labels: {detected_labels}")
        # Update the last debug time
        last_debug_time = time.time()

    if (compartment_open_detected == True and wrong_compartment_opened == True and len(detected_labels) >= 10):
        send_buzzer_notification()
    elif (compartment_open_detected == True and wrong_compartment_opened == False and len(detected_labels) >= 10):
        send_green_notification()

def find_missing_labels(day_time_slots, detected_labels):
    """
    Find the labels that are present in one list but not in the other.
    
    Args:
        day_time_slots (list): List of labels representing day and time slots.
        detected_labels (list): List of labels detected in the current frame.
    
    Returns:
        list: List of labels that are present in one list but not in the other.
    """
    missing_labels = []
    for label in day_time_slots:
        if label not in detected_labels:
            missing_labels.append(label)
    for label in detected_labels:
        if label not in day_time_slots:
            missing_labels.append(label)
    return missing_labels

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