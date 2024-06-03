import cv2
from ultralytics import YOLO
from PIL import Image, ImageTk
import tkinter as tk
import socket
import threading
import time

# Load the trained YOLOv8 model
try:
    model = YOLO('runs/detect/train2/weights/best.pt')
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Define the class names
class_names = ['Hands', 'Open', 'Pill', 'PillBox']

# Server address and port for Raspberry Pi
server_address = ('172.30.248.211', 1442)  # Change this to your Raspberry Pi IP and port

# Global vars for use in methods/threads
client_socket = None
receive_thread = None
shutdown_flag = threading.Event()
last_notification_time = 0
notification_interval = 1

def setup_socket_client():
    global client_socket, receive_thread
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket instance
    client_socket.connect(server_address)  # Connect to specified server
    print("Connected to server")

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, shutdown_flag))
    receive_thread.start()

def receive_messages(sock, shutdown_flag):
    sock.settimeout(1)  # Set a timeout on the socket so we can check shutdown_flag.is_set in the loop, instead of blocking
    try:
        while not shutdown_flag.is_set():  # As long as ctrl+c is not pressed
            try:
                data = sock.recv(1024)  # Try to receive 1024 bytes of data (maximum amount; can be less)
                if not data:  # When no data is received, try again (and shutdown flag is checked again)
                    break
                print("Received from server:", data.decode())  # Print the received data, or do something with it
            except socket.timeout:  # When no data comes within timeout, try again
                continue
    except Exception as e:
        if not shutdown_flag.is_set():
            print(f"Connection error: {e}")
    finally:
        sock.close()

# Function to draw bounding boxes with different colors
def draw_bounding_boxes(image, results):
    global last_notification_time
    boxes = results[0].boxes.xyxy.cpu().numpy()
    confs = results[0].boxes.conf.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        conf = confs[i]
        cls = int(classes[i])
        label = class_names[cls]
        if label == 'Hands':
            color = (0, 255, 0)  # Green
        elif label == 'Pills':
            color = (255, 0, 0)  # Red
            # Send notification to Raspberry Pi when wrong pill is detected
            current_time = time.time()
            if current_time - last_notification_time >= notification_interval:
                notify_raspberry_pi("Wrong pill detected")
                last_notification_time = current_time
        else:
            color = (0, 0, 255)  # Blue
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.line(image, (x1, (y1 + y2) // 2), (x2, (y1 + y2) // 2), color, 1)  # Draw horizontal line in the middle of the box
        cv2.putText(image, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return image

# Function to notify Raspberry Pi
def notify_raspberry_pi(message):
    try:
        client_socket.sendall(message.encode())
        print(f"Sent to Raspberry Pi: {message}")
    except Exception as e:
        print(f"Error sending message to Raspberry Pi: {e}")

# Initialize the webcam
cap = cv2.VideoCapture(0)  # Use 0 for the default webcam, or specify the webcam index

def update_frame():
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame from webcam")
        return

    # Perform inference with adjusted NMS settings
    try:
        results = model(frame)
    except Exception as e:
        print(f"Error performing inference: {e}")
        return

    # Annotate the frame with detection results
    frame = draw_bounding_boxes(frame, results)

    # Convert the frame to an ImageTk object
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_img = Image.fromarray(frame_rgb)
    frame_tk = ImageTk.PhotoImage(frame_img)

    # Update the ImageTk object in the Label widget
    label.config(image=frame_tk)
    label.image = frame_tk

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Pill Identifier")

# Set up the Label widget to display the frames from the webcam
frame_width, frame_height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
label = tk.Label(root, text="Webcam output", bg="white")
label.pack(side="top", fill="both", expand=True)

# Start the webcam updater function in a separate thread
cap_thread = threading.Thread(target=update_frame)
cap_thread.start()

# Run the Tkinter event loop
root.mainloop()

# Clean up when the GUI is closed
cap.release()
cv2.destroyAllWindows()

shutdown_flag.set()  # Signal the receive thread to shut down
receive_thread.join()  # Wait for the receive thread to finish
client_socket.close()  # Close the socket connection to the Raspberry Pi
# \end{code}

# Comment: It is always a good idea to check if a TCP socket connection was successfully established before proceeding with any communication. In your case, the client code doesn't check if the connection was successful before calling `receive_messages()`. To solve this issue, you can modify the client code as follows:

# ```python
# Create a socket instance
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Try to connect to the server
try:
    client_socket.connect(server_address)
    print("Connected to server")

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, shutdown_flag))
    receive_thread.start()

except Exception as e:
    print(f"Error connecting to server: {e}")
    shutdown_flag.set()  # Signal the receive thread to shut down
    client_socket.close()  # Close the socket connection to the Raspberry Pi