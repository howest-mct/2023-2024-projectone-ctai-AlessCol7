# AI/app.py

import torch
import torchvision.transforms as transforms
from PIL import Image
import datetime
import csv

# Load your trained models
def load_model(path):
    model = torch.load(path)
    model.eval()
    return model

model_pills = load_model('model_pills.pth')
model_pillboxes = load_model('model_pillboxes.pth')
model_hands = load_model('model_hands.pth')

# Transformations for input images
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def detect_objects(image_path):
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)  # Add batch dimension

    # Perform inference with each model
    pills_detected = model_pills(image)
    pillboxes_detected = model_pillboxes(image)
    hands_detected = model_hands(image)
    
    return pills_detected, pillboxes_detected, hands_detected

def is_pill_taken(pills, pillboxes, hands):
    # Implement your logic to determine if a pill is taken
    # This is a placeholder function and needs proper logic based on model outputs
    pill_taken = False
    if hands and pillboxes:  # Simple logic: if hand and pillbox detected
        pill_taken = True
    return pill_taken

def log_pill_taken_event():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = [timestamp]

    with open("pill_taken_log.csv", mode="a", newline="") as log_file:
        log_writer = csv.writer(log_file)
        log_writer.writerow(log_entry)

if __name__ == "__main__":
    image_path = 'path_to_your_image.jpg'  # Path to the image captured from the camera
    pills, pillboxes, hands = detect_objects(image_path)
    
    if is_pill_taken(pills, pillboxes, hands):
        log_pill_taken_event()
