import serial
import time
from datetime import datetime
import math
import pandas as pd
import os
import boto3
import decimal
import qrcode

# 🔗 AWS DynamoDB Configuration
AWS_REGION = "us-east-1"  # Change this if needed
DYNAMODB_TABLE = "RFID_TravelLogs"  # Change to your table name

# 🔑 AWS Credentials (Ensure AWS CLI is configured or use IAM Role)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

# 🔗 Serial Port Configuration
SERIAL_PORT = "COM6"  # Adjust based on your system
BAUD_RATE = 9600

# 📂 File Paths
LOG_FILE = "travel_log.csv"  # Local CSV log
TRAVELER_FILE = "traveller_log.csv"  # Traveler names linked with UID

# 🌍 GPS Coordinates (Example: Bangalore → Chennai)
bangalore = (12.9716, 77.5946)
chennai = (13.0827, 80.2707)

# 💰 Fare Calculation Parameters
FARE_PER_KM = 5.0  # ₹5 per km
FARE_PER_MIN = 1.0  # ₹1 per minute

# 🔄 Variables to Store Scan Details
entryUID = ""
exitUID = ""
entryTime = None
exitTime = None

# 🔍 Load Traveler Data
def load_traveler_data():
    try:
        traveler_data = pd.read_csv(TRAVELER_FILE, dtype={"UID": str})  # Ensure UID is read as string
        traveler_data.columns = traveler_data.columns.str.strip()  # Strip extra spaces
        print("✅ Traveler Data Loaded Successfully.")
        return traveler_data
    except FileNotFoundError:
        print(f"❌ Error: '{TRAVELER_FILE}' not found.")
        return pd.DataFrame(columns=["Name", "UID"])

# 🏷 Get Traveler Name by UID
def get_traveler_name(uid):
    traveler_data = load_traveler_data()
    traveler = traveler_data[traveler_data["UID"] == uid]

    if not traveler.empty:
        return traveler.iloc[0]["Name"]
    return "Unknown"

# 📏 Calculate Distance using Haversine Formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in km

# 📄 Save Travel Log to CSV
def save_travel_log(name, uid, entry_time, exit_time, distance, travel_time, fare):
    log_data = {
        "Name": [name],
        "UID": [uid],
        "Entry Time": [entry_time.strftime("%Y-%m-%d %H:%M:%S")],
        "Exit Time": [exit_time.strftime("%Y-%m-%d %H:%M:%S")],
        "Distance (km)": [round(distance, 2)],
        "Travel Time (min)": [round(travel_time, 2)],
        "Fare (INR)": [round(fare, 2)]
    }

    df = pd.DataFrame(log_data)

    if not os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, index=False)
    else:
        df.to_csv(LOG_FILE, mode='a', header=False, index=False)

    print(f"📄 Travel Log Updated: {LOG_FILE}")

# 💾 Save Travel Log to AWS DynamoDB
def save_to_dynamodb(name, uid, entry_time, exit_time, distance, travel_time, fare):
    try:
        table.put_item(
            Item={
                "UID": uid,
                "Name": name,
                "EntryTime": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                "ExitTime": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Distance_km": decimal.Decimal(str(distance)),  # Convert to Decimal
                "TravelTime_min": decimal.Decimal(str(travel_time)),  # Convert to Decimal
                "Fare_INR": decimal.Decimal(str(fare))  # Convert to Decimal
            }
        )
        print("✅ Travel log saved to DynamoDB!")
    except Exception as e:
        print(f"❌ Error saving data to DynamoDB: {e}")

# 🏦 Generate UPI QR Code for Payment
def generate_upi_qr(traveler_name, fare):
    upi_id = "sangwanmukul123@oksbi"  # Replace with your actual UPI ID

    upi_link = f"upi://pay?pa={upi_id}&pn={traveler_name}&am={fare:.2f}&cu=INR"
    qr = qrcode.make(upi_link)

    qr_filename = f"upi_qr_{traveler_name}.png"
    qr.save(qr_filename)

    print(f"✅ UPI QR Code generated: {qr_filename} (Scan to Pay)")
    return qr_filename

# 🔄 RFID Processing Function
def process_rfid():
    global entryUID, exitUID, entryTime, exitTime

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Serial Connection
        
        print("✅ Python RFID Scanner Ready...")

        while True:
            if ser.in_waiting > 0:
                uid = ser.readline().decode('utf-8').strip()

                if uid.startswith("Card UID:"):
                    card_uid = uid.split(": ")[1]  # Extract UID
                    print(f"📥 RFID Scanned: {card_uid}")

                    if not entryUID:
                        entryUID = card_uid
                        entryTime = datetime.now()
                        traveler_name = get_traveler_name(entryUID)
                        print(f"🚍 Boarding Recorded at Bangalore for {traveler_name}")
                        print(f"⏱ Entry Time: {entryTime.strftime('%Y-%m-%d %H:%M:%S')}")

                    elif not exitUID:
                        exitUID = card_uid
                        exitTime = datetime.now()
                        traveler_name = get_traveler_name(exitUID)
                        print(f"🏁 Exit Recorded at Chennai for {traveler_name}")
                        print(f"⏱ Exit Time: {exitTime.strftime('%Y-%m-%d %H:%M:%S')}")

                        travel_time = (exitTime - entryTime).total_seconds() / 60
                        distance = calculate_distance(*bangalore, *chennai)
                        fare = (distance * FARE_PER_KM) + (travel_time * FARE_PER_MIN)

                        print("\n📊 Travel Summary:")
                        print(f"👤 Traveler: {traveler_name}")
                        print(f"📍 Distance: {distance:.2f} km")
                        print(f"⏳ Travel Time: {travel_time:.2f} min")
                        print(f"💰 Fare: ₹{fare:.2f}")

                        save_travel_log(traveler_name, entryUID, entryTime, exitTime, distance, travel_time, fare)
                        save_to_dynamodb(traveler_name, entryUID, entryTime, exitTime, distance, travel_time, fare)

                        qr_code_file = generate_upi_qr(traveler_name, fare)
                        print(f"📸 Scan QR Code to Pay (File: {qr_code_file})")

                        entryUID, exitUID, entryTime, exitTime = "", "", None, None
                        print("\n🔄 Ready for Next Scan")

    except serial.SerialException as e:
        print(f"❌ Serial Error: {e}")

    except KeyboardInterrupt:
        print("🛑 Program Terminated.")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

# 🚀 Run the RFID Processing Function
process_rfid()
