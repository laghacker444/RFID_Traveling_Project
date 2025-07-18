import pandas as pd
import qrcode
import os

# 📂 Travel Log File
LOG_FILE = "travel_log.csv"

# 📸 QR Code Output File
QR_CODE_FILE = "trip_qr.png"

# 🔹 Function to Generate QR Code from Last Trip
def generate_qr_code():
    # ✅ Check if travel log exists
    if not os.path.exists(LOG_FILE):
        print("❌ No travel log found. Please scan RFID cards first!")
        return

    # 🔄 Read travel log with error handling
    try:
        df = pd.read_csv(LOG_FILE, on_bad_lines='skip')  # Skip malformed lines
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    if df.empty:
        print("❌ Travel log is empty!")
        return

    # 🏷 Get the last trip entry
    last_trip = df.iloc[-1]

    # 📝 Create trip details message
    trip_details = (
        f"🛣️ RFID Travel Details\n"
        f"👤 Name: {last_trip.get('Name', 'Unknown')}\n"
        f"📌 UID: {last_trip.get('UID', 'N/A')}\n"
        f"🕒 Entry: {last_trip.get('Entry Time', 'N/A')}\n"
        f"🏁 Exit: {last_trip.get('Exit Time', 'N/A')}\n"
        f"📍 Distance: {last_trip.get('Distance (km)', '0')} km\n"
        f"⏳ Travel Time: {last_trip.get('Travel Time (min)', '0')} min\n"
        f"💰 Fare: ₹{last_trip.get('Fare (INR)', '0')}"
    )

    # 🏷 Generate QR Code
    qr = qrcode.make(trip_details)

    # 💾 Save QR Code
    qr.save(QR_CODE_FILE)
    print(f"✅ QR Code generated: {QR_CODE_FILE}")

    # 📸 Show QR Code (Optional)
    qr.show()

# 🚀 Run QR Code Generator
generate_qr_code()
