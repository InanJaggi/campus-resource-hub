# Campus Resource Hub (AiDD 2025 Capstone)

A Flask-based MVC web application for listing, sharing, and reserving campus resources (study rooms, AV equipment, event spaces, tutoring sessions, lab instruments). Includes search, booking with conflict detection, messaging, reviews/ratings, role-based access, and admin panel. Optional: waitlist and MCP (Model Context Protocol) AI integration.

Built by a four-person team (AiDD Team 12) at Indiana University's Kelley School of Business in fall 2025. Inan Jaggi was the project lead. See [Credits](#credits).

## Features

### Core Features (Required)
✅ User Management & Authentication (Student, Staff, Admin roles)  
✅ Resource Listings (CRUD with draft/published/archived status)  
✅ Search & Filter (keyword, category, sorting: recent/most booked/top rated)  
✅ Booking & Scheduling (conflict detection, approval workflow, recurrence option)  
✅ Messaging (threaded messages between users)  
✅ Reviews & Ratings (post-booking reviews with aggregate ratings)  
✅ Admin Panel (user management, booking moderation, stats)  
✅ Simulated Email Notifications (console logging for booking events)  

### Optional Advanced Features
✅ Waitlist System (auto-enrollment on conflict, promotion on cancellation)  
✅ WCAG Accessibility (semantic HTML, ARIA labels, keyboard navigation, focus styles)  
✅ MCP AI Integration (read-only endpoints for AI agents)  
✅ AI Chatbot (Google Gemini-powered assistant for website navigation and booking help)

## Prerequisites

- **Python 3.8 or higher** (Python 3.9+ recommended)
- **pip** (Python package installer, usually comes with Python)
- **Virtual environment** (venv) - will be created during setup
- **Google Gemini API Key** (optional, for AI chatbot feature - get it from https://makersuite.google.com/app/apikey)

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# OR: source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env   # Windows: copy .env.example .env
# Add your own GEMINI_API_KEY to .env (only the chatbot needs it)

# 4. Database is already included!
# The database file (instance/campus_resource_hub.db) is included with sample data
# No initialization needed - you can start using it immediately

# 5. Run the application
python src/app.py
# OR: set FLASK_APP=src.app && flask run (Windows)
# OR: export FLASK_APP=src.app && flask run (macOS/Linux)

# 6. Open browser to http://127.0.0.1:5000/
# See "Example User Accounts" section below for login credentials
```

## Installation & Setup

### Step 1: Clone the Project

```bash
git clone https://github.com/InanJ1/campus-resource-hub.git
cd campus-resource-hub
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- Flask and Flask extensions (Login, WTF, SQLAlchemy, Bcrypt)
- SQLAlchemy for database ORM
- WTForms for form handling
- python-dotenv for environment variable management
- google-generativeai for AI chatbot
- pytest for testing
- BeautifulSoup4 and requests for testing/accessibility checks

### Step 4: Configure Environment Variables

Copy `.env.example` to `.env` and fill in your own values. `.env` is gitignored and must never be committed.
- `SECRET_KEY`: Flask secret key for sessions and CSRF protection
- `DATABASE_URL`: Database connection string (SQLite by default)
- `GEMINI_API_KEY`: Google Gemini API key for the AI chatbot feature (get one from https://makersuite.google.com/app/apikey)

Everything except the chatbot works without a Gemini key.

### Step 5: Database Setup

**The database is already included!** The project includes a pre-populated database file (`instance/campus_resource_hub.db`) with sample data, resources, bookings, and example user accounts.

**No initialization needed** - you can start using the application immediately. The database is ready to go with:
- Sample resources (study rooms, AV equipment, event spaces, etc.)
- Example bookings and reviews
- Multiple user accounts for testing (see "Example User Accounts" section below)

**Optional: Create a Fresh Database**

If you prefer to start with a clean database, you can delete `instance/campus_resource_hub.db` and run:

```bash
# Windows
set FLASK_APP=src.app
flask db-init

# macOS/Linux
export FLASK_APP=src.app
flask db-init
```

This will create a fresh database with only the default admin user (`admin@campus.edu` / `admin123`).

### Step 6: Run the Application

**Option A: Using Flask CLI (Recommended)**
```bash
# Windows
set FLASK_APP=src.app
flask run

# macOS/Linux
export FLASK_APP=src.app
flask run
```

**Option B: Direct Python execution**
```bash
python src/app.py
```

The application will start on `http://127.0.0.1:5000/`

### Step 7: Access the Application

1. Open your web browser and navigate to: `http://127.0.0.1:5000/`
2. You can:
   - Login with any of the example accounts (see "Example User Accounts" section below)
   - Register a new account (default role: `student`)
   - Browse resources, make bookings, and explore features

### Example User Accounts

The included database comes with several example user accounts you can use to explore different features and roles:

| Email | Password | Role | Description |
|-------|----------|------|-------------|
| `admin@campus.edu` | `admin123` | Admin | Full system access, user management, admin dashboard, booking logs, admin logs |
| `staff@campus.edu` | `staff123` | Staff | Can create and manage resources, approve/reject bookings for owned resources |
| `student@campus.edu` | `student123` | Student | Can browse resources, make bookings, message resource owners, leave reviews |

**Note:** These are example accounts for testing and demonstration. Feel free to use any of them to explore the application's features from different user perspectives. Each role has different permissions and access levels.

### Password Requirements

**Note:** Password requirements apply only to new user registrations. Existing accounts (including the default admin account) are not affected.

When registering a new account, passwords must meet the following requirements:
- **Minimum 8 characters**
- **At least one uppercase letter** (A-Z)
- **At least one lowercase letter** (a-z)
- **At least one number** (0-9)
- **Special character recommended** (!@#$%^&*(),.?":{}|<>)

The registration form will show real-time feedback as you type, indicating which requirements are met.

## Project Structure

```
campus-resource-hub/
├── src/
│   ├── app.py                 # Flask application factory and main entry point
│   ├── extensions.py          # Flask extensions (db, login_manager, bcrypt, csrf)
│   ├── controllers/           # Flask blueprints (MVC Controller layer)
│   │   ├── auth.py           # Authentication (login, register, logout)
│   │   ├── resources.py      # Resource management (CRUD)
│   │   ├── bookings.py       # Booking system
│   │   ├── messages.py       # Messaging system
│   │   ├── reviews.py        # Reviews and ratings
│   │   ├── admin.py          # Admin panel
│   │   ├── ai.py             # MCP AI endpoints (read-only)
│   │   └── chatbot.py        # AI chatbot endpoint
│   ├── models/               # SQLAlchemy ORM models (MVC Model layer)
│   │   └── models.py         # User, Resource, Booking, Review, Message, etc.
│   ├── views/                # Jinja2 templates (MVC View layer)
│   │   ├── auth/             # Login, register pages
│   │   ├── resources/        # Resource listing, detail, form pages
│   │   ├── bookings/         # Booking calendar, detail, my bookings
│   │   ├── messages/         # Message threads
│   │   ├── reviews/          # Review forms and listings
│   │   ├── admin/            # Admin dashboard and management pages
│   │   ├── chatbot/          # AI chatbot widget
│   │   └── errors/           # 404, 500 error pages
│   ├── data_access/          # DAL - Data Access Layer (encapsulated CRUD operations)
│   │   ├── users.py          # User data access
│   │   ├── resources.py      # Resource data access
│   │   ├── bookings.py       # Booking data access
│   │   ├── reviews.py        # Review data access
│   │   └── waitlist.py       # Waitlist data access
│   ├── utils/                # Utility functions
│   │   ├── file_upload.py    # File upload handling
│   │   └── admin_logging.py  # Admin action logging
│   └── static/               # Static files (CSS, JavaScript, images)
│       ├── css/              # Stylesheets
│       └── images/           # Image assets
├── tests/                    # Pytest test suite
│   ├── test_utils.py         # Unit tests for utility functions
│   ├── test_auth_flow.py     # Integration test: authentication
│   ├── test_dal.py           # Integration test: data access layer
│   ├── test_booking_conflict.py  # Integration test: booking conflicts
│   ├── test_waitlist.py      # Integration test: waitlist system
│   ├── test_security_sqli.py # Integration test: SQL injection prevention
│   ├── test_accessibility.py # Integration test: WCAG accessibility
│   ├── MANUAL_TEST_PLAN.md   # Manual test plan (6 test cases)
│   ├── TESTING_REFLECTION.md # Testing reflection document
│   ├── run_all_tests.py      # Master test runner
│   └── README.md             # Testing documentation
├── prompt/                   # AI-related documentation
│   ├── dev_notes.md          # AI interaction log
│   └── golden_prompts.md     # High-impact prompts
├── docs/                     # Project documentation
│   ├── er_diagram.md         # Database ER diagram
│   └── context/              # Context folders for AI
│       ├── DT/               # Design Thinking artifacts
│       └── PM/               # Product Management materials
├── instance/                 # Instance folder (database, uploaded files)
│   └── campus_resource_hub.db  # SQLite database (included with sample data)
├── .env.example              # Environment variable template (copy to .env)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Testing

### Run All Tests

```bash
# Run all tests with pytest
pytest -v

# Run all tests with the master test runner (colored output)
python tests/run_all_tests.py

# Run specific test file
pytest tests/test_auth_flow.py -v

# Run tests with coverage (if pytest-cov is installed)
pytest --cov=src --cov-report=html
```

### Test Coverage

The test suite includes:
- **Unit Tests:** 14 tests in `test_utils.py` (file upload, conflict detection, search, user retrieval)
- **Integration Tests:** 7 test files covering:
  - Authentication flow (register, login, protected routes)
  - Data Access Layer CRUD operations
  - Booking conflict detection
  - Waitlist system (enrollment and promotion)
  - SQL injection prevention
  - WCAG accessibility compliance
- **Manual Test Plan:** 6 test cases (3 positive, 3 negative) in `tests/MANUAL_TEST_PLAN.md`
  - Includes end-to-end booking flow scenarios demonstrating complete booking workflows
  - Covers positive cases (successful booking, approval, waitlist enrollment) and negative cases (conflicts, validation errors, operating hours)
  - See `tests/MANUAL_TEST_PLAN.md` for complete test scenarios, execution steps, and expected results

See `tests/README.md` for detailed testing documentation.

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | No | `dev-key-change-me` | Flask secret key for sessions and CSRF protection. Generate a secure key: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | No | `sqlite:///campus_resource_hub.db` | Database connection string. Database is created in the `instance/` folder. |
| `GEMINI_API_KEY` | Yes* | None | Google Gemini API key for AI chatbot (*required for chatbot feature). Get it from https://makersuite.google.com/app/apikey |

### Application Configuration

The application can be configured in `src/app.py`:

- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 10 MB)
- `WTF_CSRF_ENABLED`: CSRF protection (default: True)
- `TEMPLATES_AUTO_RELOAD`: Auto-reload templates in development (default: True)
- `DEBUG`: Debug mode (default: True for development)

## User Roles

- **Student**: Can browse resources, make bookings, message resource owners, and leave reviews
- **Staff**: Can create and manage resources, approve/reject bookings for their resources, and do everything students can do
- **Admin**: Full access including user management, viewing all bookings, and system administration

### Example User Accounts

The included database contains several example user accounts for testing. See the "Example User Accounts" section in Step 7 above for a complete list of available accounts and their credentials.

**Note:** The example accounts use simple passwords that don't meet the new password requirements, but they work for existing accounts. New user registrations must follow the password requirements.

## API Endpoints

For detailed API documentation with request/response examples, see `prompt/API.md`.

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - User login (creates session)
- `GET /auth/logout` - User logout

### Resources
- `GET /resources` - List/search resources (supports `?q=keyword&category=X&sort=recent|most_booked|top_rated`)
- `GET /resources/<id>` - Resource detail page
- `POST /resources` - Create resource (auth required, staff/admin only)
- `PUT /resources/<id>` - Update resource (via `/resources/<id>/edit` form)
- `DELETE /resources/<id>` - Delete resource (API endpoint, owner/admin only)

### Bookings
- `POST /bookings/new/<resource_id>` - Request new booking
- `GET /bookings/my` - User's bookings dashboard
- `GET /bookings/<id>` - Booking detail (API endpoint)
- `PUT /bookings/<id>/approve` - Approve booking (staff/admin/owner)
- `POST /bookings/<id>/cancel` - Cancel booking
- `POST /bookings/<id>/edit` - Edit booking (time, recurrence)

### Messages
- `GET /messages` - List message threads
- `GET /messages/thread/<id>` - View thread
- `POST /messages` - Send message (API endpoint, requires `thread_id` or `receiver_id`)

### Reviews
- `GET /reviews/new/<resource_id>` - Review form (requires completed booking)
- `POST /reviews` - Submit review (API endpoint)
- `GET /reviews` - List all reviews

### Admin
- `GET /admin` - Admin dashboard
- `GET /admin/stats` - Usage metrics (API endpoint, admin only)
- `POST /admin/promote/<user_id>` - Promote user to staff
- `GET /admin/users` - User management page
- `GET /admin/bookings` - Booking logs page
- `GET /admin/logs` - Admin action logs

### AI/MCP Endpoints (Read-only)
- `GET /ai/resources` - List resources (JSON, supports `?q=keyword`)
- `GET /ai/resource/<id>/schedule` - Get resource booking schedule (JSON)
- `GET /ai/resource/<id>/reviews` - Get resource reviews (JSON)

### Chatbot
- `POST /chatbot/chat` - AI chatbot endpoint (requires GEMINI_API_KEY)

**See `prompt/API.md` for complete API documentation with request/response examples.**

## Security & Privacy

- ✅ Bcrypt password hashing with salt
- ✅ CSRF protection on all forms
- ✅ Server-side validation on all inputs
- ✅ Parameterized queries via SQLAlchemy (SQL injection prevention)
- ✅ Jinja2 auto-escaping (XSS prevention)
- ✅ Limited personal data storage (email, name, role only)
- ✅ File upload size limits (10MB max)
- ✅ Role-based access control
- ✅ Secure session management with Flask-Login

## Accessibility (WCAG Compliance)

- ✅ Semantic HTML5 elements (`<main>`, `<nav>`, `<header>`, `<footer>`)
- ✅ ARIA labels and roles
- ✅ Keyboard navigation support
- ✅ High-contrast focus indicators
- ✅ Form labels properly associated
- ✅ Color contrast validation (Bootstrap defaults)
- ✅ Screen reader friendly structure

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError" when running the app

**Solution:** Make sure you've activated your virtual environment and installed dependencies:
```bash
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

#### 2. "GEMINI_API_KEY not found in environment"

**Solution:** 
1. Make sure a `.env` file exists in the project root directory (same level as `requirements.txt`). Create it from `.env.example` if it doesn't.
2. Verify the `.env` file contains a line like: `GEMINI_API_KEY=your_api_key_here`

**Note:** The chatbot feature requires this key, but the rest of the application will work without it. If the key is missing, the chatbot will show an error message, but you can still use all other features.

#### 3. "Database not initialized" or "Table doesn't exist"

**Solution:** The database should be included in the project. If you're seeing this error:
1. Check that `instance/campus_resource_hub.db` exists
2. If the database file is missing, you can create a fresh one:
   ```bash
   set FLASK_APP=src.app
   flask db-init
   ```
   This will create a new database with only the default admin user.

#### 4. "Port 5000 is already in use"

**Solution:** Either:
- Stop the other application using port 5000
- Or change the port in `src/app.py`:
  ```python
  app.run(debug=True, host="127.0.0.1", port=5001, use_reloader=True)
  ```

#### 5. "CSRF token missing" or "CSRF validation failed"

**Solution:** This usually happens when:
- The session expired (refresh the page and try again)
- The SECRET_KEY changed (restart the server)
- The form was submitted from a different domain

#### 6. Cannot login with example accounts

**Solution:** The database is included with example accounts. If you can't login:
1. Make sure `instance/campus_resource_hub.db` exists
2. Try the admin account: `admin@campus.edu` / `admin123`
3. See the "Example User Accounts" section for a complete list of available accounts
4. If the database is missing, you can create a fresh one with `flask db-init` (but it will only have the admin account)

#### 7. Images not loading

**Solution:** 
- Make sure the `src/static/images/` folder exists and contains the image files
- Check that the Flask app is serving static files correctly
- Clear your browser cache

#### 8. Tests failing

**Solution:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Make sure the database is initialized: `flask db-init`
- Run tests with verbose output: `pytest -v`

### Getting Help

If you encounter issues not listed here:
1. Check the console output for error messages
2. Check the browser console for JavaScript errors
3. Review the `prompt/dev_notes.md` for development notes
4. Check the test files for examples of how features should work

## MCP (Model Context Protocol) Integration

A read-only AI access layer is exposed via the `ai` blueprint (`/ai/*`) to safely query the SQLite database for summarization or scheduling assistance. This enables AI agents (like Cursor or Copilot) to inspect database content without modification.

**Features:**
- Resource search and listing
- Booking schedule queries
- Review aggregation
- All endpoints return JSON and are read-only

See `prompt/dev_notes.md` and `src/controllers/ai.py` for implementation details.

## AI-First Development Integration

This project follows AI-First Development practices as required by AiDD 2025, using Cursor AI as the primary development assistant throughout the project lifecycle. Our AI collaboration approach emphasizes transparency, verification, and human oversight while leveraging AI tools to accelerate development and improve code quality.

### AI-Assisted Development with Cursor

Cursor AI played a central role in our development process, assisting with architectural decisions, code generation, and problem-solving. The AI suggested the initial Data Access Layer (DAL) structure, which helped us maintain strict separation between controllers and database operations, resulting in a more maintainable and testable codebase. Cursor also assisted in implementing the MCP (Model Context Protocol) endpoints for safe, read-only database queries, and suggested the conflict detection algorithms for the booking system.

All AI contributions are documented in `prompt/dev_notes.md`, which logs all AI interactions, prompts used, and outcomes. High-impact prompts that significantly improved design or debugging are captured in `prompt/golden_prompts.md`. AI attribution comments are included in code files (e.g., `src/controllers/chatbot.py`, `src/data_access/*.py`) to mark AI-suggested code that was reviewed and modified by the team.

### Context-Aware Features

Our AI-powered features demonstrate context grounding by referencing project materials from `/docs/context/`. The AI chatbot integrates content from the Product Requirements Document (`/docs/context/PM/PRD.txt`), ensuring responses align with project objectives and stakeholder needs. The MCP endpoints (`/ai/*`) provide structured, read-only access to resource data, enabling AI agents to safely query the database for summarization or scheduling assistance. The Context Pack structure (`/docs/context/DT/`, `/docs/context/PM/`) supports AI understanding of project goals, user personas, and business context.

### Ethical AI Usage and Verification

All AI-generated code undergoes thorough review and validation before integration. We maintain strict verification processes, including comprehensive testing (unit, integration, and security tests) to catch potential issues in AI-suggested code. No fabricated data appears in AI responses—all chatbot and AI features use actual project data and context. Transparent documentation of AI assistance is maintained throughout, and human oversight is preserved at every stage of development. Our reflection on AI collaboration, including ethical considerations and lessons learned, is documented in `prompt/AI_REFLECTION.md`.

## ER Diagram

See `docs/er_diagram.md` for complete database schema.

## Development Notes

- **MVC Architecture**: Strict separation of Models, Views, and Controllers
- **DAL Pattern**: All database operations go through `data_access/` modules
- **No Raw SQL**: Controllers never issue direct SQL queries
- **AI Integration**: MCP endpoints provide safe, read-only AI access
- **Context Engineering**: `/docs/context/` supports AI reasoning about project goals

## License

This project is part of the AiDD 2025 Capstone course.

## Credits

Developed by AiDD Team 12, a four-person team, as part of the AiDD 2025 Capstone at Indiana University's Kelley School of Business, following MVC architecture, DAL patterns, and AI-First Development practices. Inan Jaggi led the project.

The sample database ships with demo accounts only. It holds no real user data.
