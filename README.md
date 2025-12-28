# ONE WORLD 3D - Backend API

Django REST Framework based backend API for ONE WORLD 3D application.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Adding Dummy Data](#adding-dummy-data)
- [Running Tests](#running-tests)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)

## ✨ Features

- **User Management & Permissions**: Organizations, Teams, Roles, Users, Invitations
- **Story Parsing**: AI-powered story parsing and structured data extraction
- **Departments**: Workspace and department management
- **Talent Pool**: Talent management and assignments
- **Art Control**: Story, sequence, and shot-level art control settings
- **Chat System**: User chat conversations
- **Cost Calculation**: Automatic cost breakdown for stories, assets, and shots

## 🛠 Tech Stack

- **Python 3.12+**
- **Django 4.2+**
- **Django REST Framework**
- **JWT Authentication** (djangorestframework-simplejwt)
- **SQLite** (Development) / **PostgreSQL** (Production)
- **CORS Headers** (for frontend integration)

## 📁 Project Structure

```
backend/
├── accounts/              # User Management & Permissions
│   ├── models.py         # User, Organization, Team, Role, Invitation models
│   ├── views.py          # Authentication views
│   ├── user_management_views.py  # User management API views
│   ├── serializers.py    # API serializers
│   ├── tests.py          # Test cases (40 tests)
│   └── management/commands/
│       ├── create_default_roles.py      # Create default roles
│       └── create_dummy_user_data.py    # Create dummy data
│
├── ai_machines/          # Story Parsing & Management
│   ├── models.py         # Story, Character, Location, Asset, Sequence, Shot, Chat
│   ├── views.py          # Story parsing, cost breakdown, art control
│   ├── chat_views.py     # Chat CRUD operations
│   ├── serializers.py    # API serializers
│   ├── tests.py          # Test cases (38 tests)
│   └── services/         # Business logic
│       ├── story_parser.py      # AI story parsing
│       └── cost_calculator.py   # Cost calculations
│
├── departments/          # Department Management
│   ├── models.py         # Department, assignments
│   ├── views.py          # Department API views
│   ├── serializers.py    # API serializers
│   ├── tests.py          # Test cases (31 tests)
│   └── management/commands/
│       └── create_default_departments.py  # Create default departments
│
├── talent_pool/          # Talent Pool Management
│   ├── models.py         # Talent, assignments
│   ├── views.py          # Talent API views
│   ├── serializers.py    # API serializers
│   ├── tests.py          # Test cases (34 tests)
│   └── management/commands/
│       └── create_default_talents.py      # Create dummy talents
│
└── oneworld3d_backend/   # Main project settings
    ├── settings.py       # Django settings
    ├── urls.py           # Main URL configuration
    └── wsgi.py           # WSGI configuration
```

## 🚀 Setup Instructions

### 1. Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### 2. Clone and Navigate

```bash
cd backend
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Environment Variables

Create a `.env` file in the `backend` directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Server will run at: `http://localhost:8000`

## 📊 Adding Dummy Data

### 1. Create Default Roles

```bash
python manage.py create_default_roles
```

This creates 6 system roles:
- Super Admin
- Admin
- Project Manager
- Artist/Contractor
- Reviewer
- Viewer

### 2. Create Dummy User Data

```bash
python manage.py create_dummy_user_data --count 20
```

This creates:
- 20 Organizations
- 20 Teams
- 20 Custom Roles
- 20 Users
- 20 Invitations

**Default Credentials:**
- Admin: `admin@oneworld3d.com` / `admin123`
- Users: `john.smith@example.com` / `test123` (and others)

### 3. Create Default Departments

```bash
python manage.py create_default_departments
```

This creates 23 default departments (Modeling, Texturing, Animation, etc.)

### 4. Create Default Talents

```bash
python manage.py create_default_talents
```

This creates 19 sample talents with various types and specializations.

## 🧪 Running Tests

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
# User Management tests (40 tests)
python manage.py test accounts.tests

# Story & AI Machines tests (38 tests)
python manage.py test ai_machines.tests

# Department tests (31 tests)
python manage.py test departments.tests

# Talent Pool tests (34 tests)
python manage.py test talent_pool.tests
```

### Run with Verbose Output

```bash
python manage.py test --verbosity=2
```

**Total Test Coverage: 143 test cases** ✅

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get JWT token)
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password

### User Management
- `GET /api/auth/users/` - List users
- `GET /api/auth/users/{id}/` - Get user details
- `PUT /api/auth/users/{id}/update/` - Update user
- `DELETE /api/auth/users/{id}/delete/` - Delete user

### Organizations
- `GET /api/auth/organizations/` - List organizations
- `POST /api/auth/organizations/` - Create organization
- `GET /api/auth/organizations/{id}/` - Get organization
- `PUT /api/auth/organizations/{id}/` - Update organization
- `DELETE /api/auth/organizations/{id}/` - Delete organization

### Teams
- `GET /api/auth/teams/` - List teams
- `POST /api/auth/teams/` - Create team
- `GET /api/auth/teams/{id}/` - Get team
- `GET /api/auth/teams/{id}/members/` - Get team members
- `POST /api/auth/teams/{id}/members/` - Add team member
- `DELETE /api/auth/teams/{id}/members/{user_id}/` - Remove member

### Roles
- `GET /api/auth/roles/` - List roles
- `POST /api/auth/roles/` - Create role
- `GET /api/auth/roles/{id}/` - Get role
- `PUT /api/auth/roles/{id}/` - Update role
- `DELETE /api/auth/roles/{id}/` - Delete role

### Invitations
- `GET /api/auth/invitations/` - List invitations
- `POST /api/auth/invitations/` - Create invitation
- `GET /api/auth/invitations/{token}/` - Get invitation by token
- `POST /api/auth/invitations/{id}/accept/` - Accept invitation
- `POST /api/auth/invitations/{id}/cancel/` - Cancel invitation

### Stories
- `POST /api/ai-machines/parse-story/` - Parse story text
- `GET /api/ai-machines/stories/` - List stories
- `GET /api/ai-machines/stories/{id}/` - Get story details
- `GET /api/ai-machines/stories/{id}/cost-breakdown/` - Get cost breakdown

### Art Control
- `GET /api/ai-machines/stories/{id}/art-control/` - Get art control settings
- `POST /api/ai-machines/stories/{id}/art-control/` - Create art control
- `PUT /api/ai-machines/stories/{id}/art-control/` - Update art control
- `DELETE /api/ai-machines/stories/{id}/art-control/reset/` - Reset art control

### Chats
- `GET /api/ai-machines/chats/` - List chats
- `POST /api/ai-machines/chats/create/` - Create chat
- `GET /api/ai-machines/chats/{id}/` - Get chat
- `PUT /api/ai-machines/chats/{id}/update/` - Update chat
- `DELETE /api/ai-machines/chats/{id}/delete/` - Delete chat

### Departments
- `GET /api/departments/` - List departments
- `POST /api/departments/` - Create department
- `GET /api/departments/{id}/` - Get department
- `PUT /api/departments/{id}/` - Update department
- `DELETE /api/departments/{id}/` - Delete department

### Talent Pool
- `GET /api/talent-pool/talent/` - List talents
- `POST /api/talent-pool/talent/` - Create talent
- `GET /api/talent-pool/talent/{id}/` - Get talent
- `PUT /api/talent-pool/talent/{id}/` - Update talent
- `DELETE /api/talent-pool/talent/{id}/` - Delete talent

## 🔐 Authentication

All API endpoints (except register/login) require JWT authentication.

**Request Header:**
```
Authorization: Bearer <your-jwt-token>
```

**Get Token:**
```bash
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `EMAIL_HOST` | SMTP server | Optional |
| `EMAIL_PORT` | SMTP port | Optional |
| `EMAIL_HOST_USER` | Email username | Optional |
| `EMAIL_HOST_PASSWORD` | Email password | Optional |
| `FRONTEND_URL` | Frontend URL for CORS | Yes |

## 🐛 Troubleshooting

### Migration Issues

```bash
# Delete migrations and recreate
python manage.py makemigrations
python manage.py migrate
```

### Database Reset

```bash
# Delete database file
rm db.sqlite3

# Recreate migrations
python manage.py makemigrations
python manage.py migrate

# Add dummy data again
python manage.py create_default_roles
python manage.py create_dummy_user_data --count 20
python manage.py create_default_departments
python manage.py create_default_talents
```

### Port Already in Use

```bash
# Use different port
python manage.py runserver 8001
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is proprietary software.

---

**Happy Coding! 🚀**

