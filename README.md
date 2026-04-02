# 🎓 UniVent – University Event & Club Management System

A web-based platform designed to streamline and digitize the management of student clubs and events within a university.

---

## 📌 Overview

UniVent is a centralized **Club Management System** that helps students, club heads, and administrators efficiently manage:

- Event creation & approvals  
- Student registrations  
- Club memberships  
- Resource allocation  
- Participation tracking  

The system replaces manual processes with an automated, scalable solution.

> Based on DBMS mini project developed at MIT-WPU.

---

## 🚨 Problem Statement

Managing college clubs manually leads to:

- Disorganized event planning  
- Delayed approvals  
- Poor communication  
- Lack of centralized records  

UniVent solves these problems by providing a **single digital platform** for all club activities. :contentReference[oaicite:0]{index=0}

---

## 💡 Key Features

### 👨‍🎓 Student Module
- View upcoming events  
- Register for events  
- Track registered events  
- Explore clubs  

### 👑 Club President Module
- Create & manage events  
- View participants  
- Manage members  
- Generate reports  

### 🛠️ Admin Module
- Approve/reject events  
- Manage hall bookings  
- Allocate resources  
- Monitor system activity  

---

## 🗄️ Database Design

The system uses a structured relational database with key tables:

- Users  
- Clubs  
- Events  
- Memberships  
- Event Registrations  
- Resource Requests  
- Approvals  

> The ER Diagram (see report page 7) defines relationships between users, events, and resources.

---

## 🛠️ Tech Stack

### Frontend
- HTML  
- CSS  
- JavaScript  

### Backend
- Flask / PHP (based on implementation version)  
- MySQL  

---

## 📊 System Modules

### 🔐 Login System
- Secure authentication  
- Role-based access control  

### 📊 Dashboard System
- Student dashboard  
- Club dashboard  
- Admin dashboard  

### 📅 Event Management
- Create events  
- Approval workflow  
- Event tracking  

### 📦 Resource Management
- Request resources  
- Allocation system  
- Availability tracking  

---

## 📈 Results

The system successfully demonstrates:

- Event approval workflow  
- Student event registration  
- Email notifications  
- Real-time dashboards  

(Refer to report pages 16–17 for screenshots)

---

## 🚀 Future Enhancements

- 📱 Mobile app integration  
- 📊 Analytics dashboard  
- 🤖 AI-based event reports  
- 🔔 Smart notifications  
- 📅 Calendar sync  

---

## 🎯 Conclusion

UniVent provides a scalable and efficient solution for managing university clubs.  
It demonstrates practical implementation of:

- ER Modeling  
- Database normalization  
- SQL-based systems  

The system improves **transparency, efficiency, and student engagement**. :contentReference[oaicite:1]{index=1}

---

## 👥 Team Members

- Arnav Nikumbh  
- Divya Yokar  
- Rishi Raj Thakur  
- Naitri Panchal  

---

## 🎓 Institution

MIT World Peace University, Pune  
Department of Computer Engineering & Technology  

---

## ⭐ How to Run the Project

```bash
# Clone the repo
git clone https://github.com/your-username/CareerLens.git

# Go to project folder
cd CareerLens-main

# Install dependencies (if Flask)
pip install -r requirements.txt

# Run server
python app.py
# 1. Clone the repository
git clone https://github.com/your-username/UniVent.git

# 2. Navigate to the project directory
cd UniVent

# 3. Create a virtual environment (recommended)
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup MySQL Database
# - Create a database (e.g., univent_db)
# - Import the SQL file provided in the project

# Example:
mysql -u root -p
CREATE DATABASE univent_db;
USE univent_db;
SOURCE database.sql;

# 6. Configure environment variables / DB credentials
# Update in config file (app.py or config.py):
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=univent_db

# 7. Run the Flask application
python app.py
