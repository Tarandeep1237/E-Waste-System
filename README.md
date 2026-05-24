♻️ EcoAI: AI-Driven E-Waste Collection System

Smart • Sustainable • AI-Powered Recycling
An intelligent AI-powered platform that simplifies electronic waste collection, classification, scheduling, and route optimization for efficient and eco-friendly recycling.

📖 Overview
EcoAI is a full-stack AI-driven E-Waste Collection System developed to modernize and simplify electronic waste recycling operations.
The system allows users to upload images of electronic waste, automatically classify them using Machine Learning, schedule pickups, and earn eco-reward points for responsible recycling.
Administrators can efficiently manage pickup requests, monitor analytics, and optimize collection routes using route optimization algorithms.

✨ Features
🧠 AI-Based E-Waste Classification
Upload images of electronic waste
TensorFlow model predicts waste category automatically
Supports classification of:
Smartphones
Laptops
Electronic Accessories
Home Appliances
Other E-Waste Items

📅 Smart Pickup Scheduling
Easy pickup booking system
Schedule pickups based on user convenience
Real-time request management

🎁 Eco Reward System
Users receive eco-points after successful recycling
Encourages sustainable waste disposal practices

🔐 Secure Authentication System
JWT-based authentication
Password encryption using Bcrypt
Secure user login and registration

🗺️ Route Optimization
Uses Nearest Neighbor Algorithm
Optimizes collection routes for administrators
Reduces transportation cost and time

📊 Admin Dashboard
View booking analytics
Manage user requests
Approve or reject pickups
Monitor recycling activities

🛠️ Tech Stack
Frontend
Technology	Purpose
HTML5	Structure
CSS3	Styling & Glassmorphism UI
JavaScript	Client-side functionality
Chart.js	Analytics Visualization
Leaflet.js	Maps & Location Tracking
Backend
Technology	Purpose
Flask	REST API Backend
Python	Core Programming Language
MySQL	Database Management
JWT	Authentication
Bcrypt	Password Hashing
AI / Machine Learning
Technology	Purpose
TensorFlow	Model Training & Prediction
Keras	Deep Learning API
OpenCV	Image Processing
Pillow	Image Handling

🏗️ System Architecture
User Uploads E-Waste Image
            ↓
Frontend Interface
            ↓
Flask Backend API
            ↓
TensorFlow ML Model
            ↓
Waste Classification
            ↓
Pickup Scheduling
            ↓
Admin Dashboard & Route Optimization

📂 Project Structure
E-Waste-System/
│
├── backend/
│   ├── ml/                     # Machine Learning models
│   ├── route_opt/              # Route optimization algorithms
│   ├── routes/                 # API route definitions
│   ├── utils/                  # Utility/helper functions
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   └── seed_sample_data.py     # Sample database records
│
├── frontend/
│   ├── static/                 # CSS & JavaScript files
│   ├── admin.html              # Admin dashboard
│   ├── index.html              # Landing page
│   └── register.html           # Login/Register page
│
├── tests/                      # Unit testing
├── requirements.txt            # Python dependencies
├── README.md
└── .gitignore

🚀 Installation & Setup
🔹 Prerequisites

Ensure the following software is installed:

Python 3.8+
MySQL Server
Git
VS Code (Recommended)
🔹 Clone Repository
git clone https://github.com/Tarandeep1237/E-Waste-System.git
cd E-Waste-System
🔹 Create Virtual Environment
python -m venv venv
Activate Environment
Windows
venv\Scripts\activate
Linux / macOS
source venv/bin/activate
🔹 Install Dependencies
pip install -r requirements.txt
🔹 Configure Database

Create MySQL Database:

CREATE DATABASE ewaste_db;

Update database credentials inside:

backend/config.py

Seed sample data:
cd backend
python seed_sample_data.py
🔹 Run Backend Server
python app.py
Backend runs at:
http://localhost:5000
🔹 Run Frontend

Open:
frontend/index.html
or use Live Server Extension in VS Code.

💻 Application Workflow
👤 User Side
Register/Login
Upload E-Waste Image
AI predicts waste category
Schedule pickup request
Earn eco reward points

🛡️ Admin Side
Login to Admin Dashboard
View pickup requests
Optimize collection routes
Manage users & analytics
Monitor recycling activities

🌱 Future Enhancements
📱 Mobile Application Support
☁️ Cloud Deployment using Docker
🔔 Real-Time Pickup Notifications
📍 Live Vehicle Tracking
🤖 Advanced AI Waste Suggestions
🧾 QR-Based Reward System
🤝 Contributing

📝 License
This project is licensed under the MIT License.
