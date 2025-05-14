# College Management System

A comprehensive Django-based College Management System with features for managing students, staff, courses, attendance, assignments, and fee payments.

## Features

- User Authentication and Authorization
- Student Management
- Staff Management
- Course and Subject Management
- Attendance Tracking
- Assignment Management
- Fee Management with Razorpay Integration
- Leave Management
- Result Management
- Notification System
- Feedback System

## Technology Stack

- Python 3.x
- Django 3.x
- Bootstrap 4
- jQuery
- SQLite (Development) / PostgreSQL (Production)
- Razorpay Payment Gateway

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CollegeManagement-Django.git
cd CollegeManagement-Django
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the project root and add:
```
DEBUG=True
SECRET_KEY=your_secret_key
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the admin panel at `http://localhost:8000/admin`
2. Login with superuser credentials
3. Add courses, subjects, staff, and students
4. Staff can manage attendance, assignments, and results
5. Students can view their attendance, assignments, and pay fees

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 