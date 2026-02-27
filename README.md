# 🏥 Clinic Appointment System

A role-based clinic management system built with **Django** and **PostgreSQL** that allows patients to book appointments, receptionists to manage scheduling, and doctors to manage consultations with proper permissions and workflows.

---

## 📖 API Documentation

You can view all APIs interactively using **Swagger Editor**.

### Steps:

1. Open **Swagger Editor** in your browser:  
   [https://editor.swagger.io/](https://editor.swagger.io/)

2. Open or paste the `swagger.yaml` file from this project:  
   [swagger.yaml](https://github.com/Besso2003/Clinic_Appointment_System_Python/blob/main/swagger.yaml)

3. You’ll see **all endpoints categorized by app**:
   - `Accounts` → User registration, login, profile
   - `Scheduling` → Doctor availability & slot generation
   - `Appointments` → Booking, lifecycle, check-in, rescheduling
   - `MedicalRecords` → Consultation records & prescriptions
   - `Dashboard` → Admin analytics & user management

### Notes:
- Any new endpoints added to the project should be updated in the Swagger file immediately.  

---

## 📌 Features

### 👤 Patient

* Register & login
* View and update profile
* Book available appointment slots
* View upcoming & past appointments
* Cancel or request reschedule
* View consultation summary (read-only)

### 👨‍⚕️ Doctor

* View schedule & daily queue
* Confirm/decline appointments
* Mark: checked-in, completed, no-show
* Fill consultation record (diagnosis, notes, prescriptions, tests)

### 🧑‍💼 Receptionist

* Manage doctor schedules & availability
* Confirm bookings
* Check-in patients & manage queue
* Reschedule appointments
* ❌ Cannot access medical notes

### 🛠️ Admin

* Manage users & roles
* Analytics dashboard
* Export reports (CSV)

---

## 🧱 Project Structure

```
Clinic_Appointment_System_Python/
│
├── accounts/            # Users, roles, profiles
├── scheduling/          # Doctor availability & slot generation
├── appointments/        # Booking, lifecycle, queue, rescheduling
├── medical_records/     # Consultation records & prescriptions
├── dashboard/           # Analytics & admin dashboard
│
├── clinic_system/       # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
│
├── templets/      
│   ├── accounts/         
│   ├── scheduling/        
│   ├── appointments/      
│   ├── medical_records/     
│   ├── dashboard/  
│   └── base.html
│
├── static/      
│   └── css/
│       └──style.css
│
├── .env
├── .gitignore    
├── .env.example         # Environment variables template
├── requirements.txt
├── manage.py
└── README.md
```

---

## ⚙️ Tech Stack

* **Backend:** Django, Django REST Framework
* **Database:** PostgreSQL
* **Auth:** Django Authentication + Groups
* **Environment:** python-decouple
* **Version Control:** Git & GitHub

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Besso2003/Clinic_Appointment_System_Python.git
cd Clinic_Appointment_System_Python
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / Mac**

```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create `.env` file in project root like `.env.example`:

```env
DB_NAME=clinic_db
DB_USER=clinic_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_secret_key
```

---

### 5️⃣ Setup PostgreSQL Database

Create database and user:

```sql
CREATE DATABASE clinic_db;
CREATE USER clinic_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE clinic_db TO clinic_user;
```

---

### 6️⃣ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 7️⃣ Run Development Server

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

---

## 🔐 Roles & Permissions

The system uses **Django Groups**:

* Patient
* Doctor
* Receptionist
* Admin

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 👥 Team Workflow

### Branch Strategy

* `main` → stable
* `mustafa` → personal branch
* `yasser` → personal branch
* `yassin` → personal branch
* `ibrahim` → personal branch
* `bassant` → personal branch

### Basic Flow

```bash
git checkout -b name
git commit -m "message"
git push -u origin name

git checkout main
git pull origin main
git merge name
git push origin main
```

---

## 🤝 Contributors

* Mustafa Tarek
* Ahmed Yasser
* Yassin
* Ibrahim
* Bassant
---
