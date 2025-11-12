# ONE WORLD 3D - Backend

Django REST Framework backend for ONE WORLD 3D platform.

## 🚀 Tech Stack

- **Django 5.2.8** - Web Framework
- **Django REST Framework 3.16.1** - API Framework
- **Django REST Framework SimpleJWT 5.5.1** - JWT Authentication
- **Django CORS Headers 4.9.0** - CORS Support
- **OpenAI 2.7.2** - GPT-4 API for Story Parsing
- **python-dotenv 1.2.1** - Environment Variables Management

## 📁 Project Structure

```
backend/
├── accounts/              # User authentication & management
│   ├── models.py         # Custom User model
│   ├── serializers.py    # User serializers
│   ├── views.py          # Authentication views
│   └── urls.py           # Auth URLs
├── ai_machines/          # Story Parsing with GPT-4
│   ├── models.py         # Story, Character, Location, Asset, Shot models
│   ├── views.py          # Story parsing API
│   ├── urls.py           # Story parsing URLs
│   └── services/
│       └── story_parser.py  # GPT-4 story parsing service
├── oneworld3d_backend/   # Main project
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL routing
│   └── wsgi.py           # WSGI config
├── manage.py
├── requirements.txt
├── .env                  # Environment variables (OPENAI_API_KEY)
└── README.md
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)
- OpenAI API Key

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API Key
# Windows (PowerShell):
$env:OPENAI_API_KEY="your-api-key-here"
# Or create .env file in backend directory:
# OPENAI_API_KEY=your-api-key-here

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The server will run at `http://localhost:8000`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile

### Story Parsing
- `POST /api/ai-machines/parse-story/` - Parse story/script using GPT-4
  - **Body:**
    ```json
    {
      "story_text": "Your story content here..."
    }
    ```
  - **Response:**
    ```json
    {
      "story_id": 1,
      "parsed_data": {
        "summary": "Story summary",
        "total_shots": 6,
        "estimated_total_time": "10-15 days",
        "characters": [...],
        "locations": [...],
        "assets": [...],
        "shots": [...]
      },
      "message": "Story parsed successfully"
    }
    ```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## ⚙️ Configuration

### Settings

Key configurations in `settings.py`:

- **CORS**: Allowed origins for React frontend (`http://localhost:3000`)
- **JWT**: Token lifetime and refresh settings
- **REST Framework**: Default authentication and permissions
- **Database**: SQLite (default, can be changed to PostgreSQL)

### Environment Variables

**Required:**
- `OPENAI_API_KEY` - OpenAI API key for GPT-4 story parsing

**Setting OpenAI API Key:**

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Or create a `.env` file in the backend directory:**
```
OPENAI_API_KEY=your-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

## 🗄️ Database

Default database is SQLite (`db.sqlite3`). For production, use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'oneworld3d',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📝 Features

### Current Features
1. ✅ User Registration & Login (JWT Authentication)
2. ✅ Story Parsing with GPT-4
   - Extracts Characters
   - Extracts Locations
   - Extracts Assets
   - Extracts Shots with complexity
   - Provides summary and time estimates

### Database Models
- **User** - Custom user model (email-based authentication)
- **Story** - Parsed stories
- **Character** - Characters extracted from stories
- **Location** - Locations extracted from stories
- **StoryAsset** - Assets extracted from stories
- **Shot** - Shots extracted from stories

## 🤝 Development

For development, make sure your React frontend is running on `http://localhost:3000` for CORS to work properly.

## 📦 Dependencies

See `requirements.txt` for full list of dependencies.

---

**Status:** ✅ Minimal Setup - Register/Login + Story Parsing
