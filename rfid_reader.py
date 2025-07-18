import serial
import pandas as pd
import cv2
import time

# Load Faculty Database
faculty_db = pd.read_csv("faculty_db.csv")

# Connect to Arduino (Update COM port if needed)
try:
    arduino = serial.Serial("COM6", 9600, timeout=1)  # Windows: "COMx", Linux: "/dev/ttyUSB0"
    time.sleep(2)  # Allow Arduino time to reset
    arduino.flush()  # Clear any existing input buffer
    print("✅ Arduino Connected Successfully!")
except serial.SerialException:
    print("❌ Failed to connect to Arduino. Check the COM port.")
    exit()

def get_faculty_class(rfid):
    """Fetch faculty details from the database using RFID"""
    faculty_info = faculty_db[faculty_db["Faculty RFID"] == rfid]
    if not faculty_info.empty:
        faculty_name = faculty_info["Faculty Name"].values[0]
        class_name = faculty_info["Class Name"].values[0]
        print(f"✅ Faculty Identified: {faculty_name} | Class: {class_name}")
        return class_name
    else:
        print("❌ Unknown Faculty RFID")
        return None

def capture_image():
    """Capture an image of the class using the laptop's camera"""
    cam = cv2.VideoCapture(0)
    time.sleep(2)  # Give the camera time to warm up
    ret, frame = cam.read()

    if not ret:
        print("❌ Failed to capture image")
        return None

    image_path = "class_image.jpg"
    cv2.imwrite(image_path, frame)
    print("✅ Image Captured Successfully!")
    cam.release()
    cv2.destroyAllWindows()

    return image_path

print("📡 Waiting for RFID scan...")

while True:
    try:
        if arduino.in_waiting > 0:
            rfid = arduino.readline().decode("utf-8", errors="ignore").strip()
            
            if rfid:
                print(f"📌 RFID Received: {rfid}")
                class_name = get_faculty_class(rfid)
                
                if class_name:
                    image_path = capture_image()
                    if image_path:
                        print("✅ Attendance Processing Initiated!")
                        break  # Exit loop and move to next step

    except serial.SerialException:
        print("❌ Serial communication error. Check Arduino connection.")
        break
