# Django API Project

## Overview
This project is a Django-based API application that utilizes Django Rest Framework for building RESTful APIs. It includes user accounts and project management features with OneToMany and ManyToMany relationships in its data models.

## Project Structure
```
django-api-project
├── myproject
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps
│   ├── __init__.py
│   ├── accounts
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   └── tests.py
├── templates
│   ├── base.html
│   └── accounts
│       └── ...
├── static
│   ├── css
│   ├── js
│   └── images
├── media
├── requirements.txt
├── manage.py
├── .gitignore
├── ruff.toml
└── README.md
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd django-api-project
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**
   Update the `DATABASES` setting in `myproject/settings.py` to match your database configuration.

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the API Documentation**
   The API documentation is available at `/api/docs/` after running the server.

## Features
- User authentication and management through the accounts app.
- Project management features implemented in the accounts app.
- RESTful API endpoints with Swagger documentation.
- Custom validation in forms.
- Automated tests for key functionalities.

## Testing
To run the tests, use the following command:
```bash
python manage.py test
```

## Linting
This project uses Ruff for linting. To run the linter, execute:
```bash
ruff check .
```

## Media Files
Uploaded media files will be stored in the `media` directory, configured as `MEDIA_ROOT` in `settings.py`.

## License
This project is licensed under the MIT License. See the LICENSE file for details.