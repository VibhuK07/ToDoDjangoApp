# Advanced ToDo App with Project Management

[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red)](https://www.django-rest-framework.org/)

A feature-rich task management system with project collaboration capabilities, built with Django REST Framework.

## Features

- 🔐 **Secure Authentication**  
  Token-based user registration/login
- 📂 **Project Organization**  
  Create projects with titles/descriptions
- ✅ **Nested Tasks**  
  Unlimited subtask hierarchy
- ⚙️ **Smart Dependencies**  
  AND/OR logical dependencies between tasks
- 📅 **Automated Scheduling**  
  Intelligent task scheduling based on dependencies
- 👥 **Collaboration**  
  Task assignment and role-based access control

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation
```bash
# Clone repository
git clone https://github.com/VibhuK07/ToDoDjangoApp.git
cd ToDoDjangoApp

# Install dependencies
pip install -r requirements.txt

# Configure database
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run server
python manage.py runserver
