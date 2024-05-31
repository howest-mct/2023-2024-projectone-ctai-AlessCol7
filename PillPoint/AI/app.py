import cv2
from ultralytics import YOLO

# Print camera properties for debugging
def print_camera_properties(cap):
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    fourcc_str = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)]) if fourcc != 0 else "Unknown"
    print(f"Frame width: {width}")
    print(f"Frame height: {height}")
    print(f"FPS: {fps}")
    print(f"FourCC: {fourcc_str}")

# Load the custom YOLOv8 model
model = YOLO('runs/detect/train2/weights/best.pt')

# Try different indices and backends to ensure the correct webcam is used
backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_V4L2]
successful_open = False

for index in range(5):  # Try more indices
    for backend in backends:
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            print(f"Successfully opened webcam with index {index} and backend {backend}")
            print_camera_properties(cap)  # Print camera properties
            successful_open = True
            break
    if successful_open:
        break
else:
    print("Error: Could not open any webcam.")
    exit()

# Main loop for capturing frames and performing inference
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Perform inference
    results = model(frame)

    # Display the results on the frame
    for result in results:
        for box in result.boxes:
            coords = box.xyxy[0].tolist()
            if len(coords) == 4:
                x1, y1, x2, y2 = map(int, coords)
                conf = box.conf[0]
                cls = box.cls[0]
                class_name = model.names[int(cls)]
                label = f'{class_name} {conf:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                print("Unexpected coordinates format:", coords)

    # Display the frame
    cv2.imshow('Webcam Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
