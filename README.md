# EcoAI: AI-Driven E-Waste Collection System

**Smart, Sustainable, and AI-Powered Recycling**

An intelligent AI-powered platform that simplifies electronic waste collection, classification, scheduling, and route optimization for efficient and eco-friendly recycling.

## 1. Overview

EcoAI is a full-stack AI-driven E-Waste Collection System developed to modernize and simplify electronic waste recycling operations.

The system allows users to:

- Upload images of electronic waste.
- Automatically classify e-waste using Machine Learning.
- Schedule pickup requests.
- Earn eco-reward points for responsible recycling.

Administrators can efficiently:

- Manage pickup requests.
- Monitor analytics.
- Optimize collection routes.
- Improve recycling operations.

## 2. Key Features

### 2.1 AI-Based E-Waste Classification

- Upload images of electronic waste.
- TensorFlow model predicts the waste category automatically.
- Supports classification of:
  - Smartphones
  - Laptops
  - Electronic Accessories
  - Home Appliances
  - Other E-Waste Items

### 2.2 Smart Pickup Scheduling

- Easy pickup booking system.
- Schedule pickups based on user convenience.
- Real-time request management.

### 2.3 Eco Reward System

- Users receive eco-points after successful recycling.
- Encourages sustainable waste disposal practices.

### 2.4 Secure Authentication System

- JWT-based authentication.
- Password encryption using Bcrypt.
- Secure user login and registration.

### 2.5 Route Optimization

- Uses the Nearest Neighbor Algorithm.
- Optimizes collection routes for administrators.
- Reduces transportation cost and time.

### 2.6 Admin Dashboard

- View booking analytics.
- Manage user requests.
- Approve or reject pickups.
- Monitor recycling activities.

## 3. Technology Stack

### 3.1 Frontend

| Technology | Purpose |
|---|---|
| HTML5 | Structure |
| CSS3 | Styling and Glassmorphism UI |
| JavaScript | Client-side functionality |
| Chart.js | Analytics visualization |
| Leaflet.js | Maps and location tracking |

### 3.2 Backend

| Technology | Purpose |
|---|---|
| Flask | REST API backend |
| Python | Core programming language |
| MySQL | Database management |
| JWT | Authentication |
| Bcrypt | Password hashing |

### 3.3 AI and Machine Learning

| Technology | Purpose |
|---|---|
| TensorFlow | Model training and prediction |
| Keras | Deep learning API |
| OpenCV | Image processing |
| Pillow | Image handling |

## 4. System Architecture

EcoAI follows a modular architecture that integrates the frontend, Flask backend, Machine Learning model, database, and administrative features.

**System Flow:**

```text
User Uploads E-Waste Image
          |
          v
Frontend Interface
          |
          v
Flask Backend API
          |
          v
TensorFlow ML Model
          |
          v
Waste Classification
          |
          v
Pickup Scheduling
          |
          v
Admin Dashboard and Route Optimization
```

## 5. Project Structure

```text
E-Waste-System/
│
├── backend/
│   ├── ml/                  # Machine Learning models
│   ├── route_opt/           # Route optimization algorithms
│   ├── routes/              # API route definitions
│   ├── utils/               # Utility and helper functions
│   ├── app.py               # Main Flask application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   └── seed_sample_data.py  # Sample database records
│
├── frontend/
│   ├── static/              # CSS and JavaScript files
│   ├── admin.html           # Admin dashboard
│   ├── index.html           # Landing page
│   └── register.html        # Login and registration page
│
├── tests/                   # Unit testing
├── requirements.txt         # Python dependencies
├── README.md
└── .gitignore
```

## 6. Installation and Setup

### 6.1 Prerequisites

Ensure the following software is installed:

- Python 3.8+
- MySQL Server
- VS Code (Recommended)

### 6.2 Clone Repository

```bash
git clone https://github.com/Tarandeep1237/E-Waste-System.git

cd E-Waste-System
```

### 6.3 Create Virtual Environment

```bash
python -m venv venv
```

### 6.4 Activate Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 6.5 Install Dependencies

```bash
pip install -r requirements.txt
```

### 6.6 Configure Database

Create the MySQL database:

```sql
CREATE DATABASE ewaste_db;
```

Update the database credentials inside:

```text
backend/config.py
```

Seed sample data:

```bash
cd backend

python seed_sample_data.py
```

### 6.7 Run Backend Server

```bash
python app.py
```

Backend runs at:

```text
http://localhost:5000
```

### 6.8 Run Frontend

Open the following file in a browser:

```text
frontend/index.html
```

Alternatively, use the Live Server Extension in VS Code.

## 7. Application Workflow

### 7.1 User Side

1. Register or log in.
2. Upload an e-waste image.
3. AI predicts the waste category.
4. Schedule a pickup request.
5. Earn eco-reward points after successful recycling.

### 7.2 Admin Side

1. Log in to the Admin Dashboard.
2. View pickup requests.
3. Optimize collection routes.
4. Manage users and analytics.
5. Monitor recycling activities.

## 8. Future Enhancements

- Mobile application support.
- Cloud deployment using Docker.
- Real-time pickup notifications.
- Live vehicle tracking.
- Advanced AI waste suggestions.
- QR-based reward system.

## 9. License

This project is licensed under the MIT License.

## 10. Author

**Tarandeep Singh**

AI/ML Engineering Student

Developed as an AI-driven sustainability project integrating Machine Learning, full-stack development, secure authentication, and route optimization to improve electronic waste collection and recycling operations.
