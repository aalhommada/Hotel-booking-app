# Hotel Management System

A Django-based hotel management system with room booking, user management, and administrative features.

## Features

- User Management (Admin, Manager, Team, Customer)
- Room Management
- Booking System
- Image Gallery
- Dynamic Room Search & Filtering
- Role-based Access Control
- Responsive Design

## Tech Stack

- Backend: Django
- Frontend: HTML, CSS (Tailwind), JavaScript
- Database: SQLite (default)
- Additional: HTMX for dynamic interactions

## Prerequisites

- Python 3.10+
- pip
- virtualenv or venv

## Installation

1. Clone the repository
```bash
git clone [repository-url]
cd hotel_management
```

2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create environment file
```bash
# Copy example environment file
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Create necessary groups and permissions
```bash
python manage.py setup_groups
```

8. Run the development server
```bash
python manage.py runserver
```

## Environment Variables

Copy `.env.example` to `.env` and update the values:
- `DEBUG`: Set to False in production
- `SECRET_KEY`: Your Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Your database URL (if using different database)

## Project Structure

```
hotel_management/
├── manage.py
├── requirements.txt
├── .env.example
├── .env                    # Create from .env.example
├── hotel_management/       # Project configuration
├── static/                # Static files
├── media/                 # User uploaded files
├── templates/             # Project templates
├── accounts/              # User management
├── rooms/                 # Room management
├── bookings/             # Booking system
└── core/                 # Core functionality
```

## User Roles

1. Admin
   - Full system access
   - User management
   - System configuration

2. Manager
   - Room management
   - Booking management
   - Report access

3. Team
   - Booking management
   - Basic room management

4. Customer
   - Room browsing
   - Booking creation
   - Profile management

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines for Python code.

### Making Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[License Type] - MIT

## Contact

Your Name - [aalhommada@gmail.com]

Project Link: [repository-url]
