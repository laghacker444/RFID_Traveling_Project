# RFID_Traveling_Project
A smart RFID-based fare management system using GPS, cloud (AWS DynamoDB), and real-time QR code payments. It calculates fare via Haversine formula, logs travel data locally and to the cloud, and enables UPI payments. Arduino-based validation ensures secure, cashless transit with live fare display.

This Project presents a smart and secure RFID-based travel fare management system integrated with cloud computing and real-time QR code payment generation. The system automates travel logging by capturing RFID card scans at entry and exit points, calculating journey distance and duration using predefined GPS coordinates, and computing the fare based on dynamic parameters such as distance (via Haversine formula) and time. The logs are stored locally in CSV format and concurrently uploaded to AWS DynamoDB for cloud-based storage, ensuring data persistence and accessibility. To streamline fare transactions, the system generates UPI-compatible QR codes for each travel session, facilitating instant digital payments. A complementary Arduino-based embedded system validates RFID tags in physical transit stations, displaying real-time travel and fare data on an LCD and ensuring passenger identity consistency through UID verification. This end-to-end system provides a reliable, scalable, and cashless solution for public transport fare collection, enhancing transparency, security, and user convenience. The proposed framework demonstrates the fusion of IoT, embedded systems, and cloud technologies to build next-generation intelligent transport solutions.
Keywords :- RFID-based Fare Management , IoT in Public Transport , Cloud Computing , Arduino Embedded System , Smart Transit Solutions 

<img width="925" height="714" alt="image" src="https://github.com/user-attachments/assets/63ec551e-534a-4651-b8f2-af158a67c81a" />


Video link:- https://youtu.be/y4rTBh54myQ?feature=shared
