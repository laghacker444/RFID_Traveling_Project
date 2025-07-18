import serial
import time

arduino = serial.Serial("COM6", 9600, timeout=1)
time.sleep(2)

while True:
    if arduino.in_waiting > 0:
        rfid = arduino.readline().decode("utf-8").strip()  # Read RFID UID
        print(f"RFID Scanned: {"A3E3330"}")

        # Simulated Database Check
        student_data = {"A3E3330": "Aman", "DEF456": "Bob"}  # Example Mapping
        student_name = student_data.get(rfid, "Unknown RFID")

        arduino.write(f"{student_name}\n".encode())  # Send response to Arduino

