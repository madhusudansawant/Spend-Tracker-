# Mini Spend Tracker

A full-stack personal expense tracking application built with Django REST Framework, PostgreSQL, and a responsive HTML/CSS/JavaScript frontend.

The application provides JWT-based authentication, expense management, filtering, monthly spending summaries, and spending insights.

---

## Tech Stack

### Backend

* Python
* Django
* Django REST Framework
* PostgreSQL
* JWT Authentication

### Frontend

* HTML5
* CSS3
* JavaScript

### Database

* PostgreSQL
* Supabase PostgreSQL

### Deployment

* Render

---

## Features

* User registration
* JWT login and authentication
* JWT access and refresh tokens
* Create expenses
* List expenses
* Filter expenses by category
* Filter expenses by date range
* Monthly total spending
* Spending by category
* Previous month spending
* Month-over-month spending change
* Category spending insights when spending increases by more than 20%
* Input validation
* Error handling
* User-based data isolation
* Automated backend tests
* Responsive frontend UI

---

## Project Structure

```text
spend-tracker/

├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   ├── accounts/
│   └── expenses/
│
├── frontend/
│   ├── index.html
│   ├── CSS/
│   │   └── style.css
│   └── JS/
│       └── app.js
│
├── .gitignore
└── README.md
```

---

## API Endpoints

### Authentication

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
```

### Expenses

```text
POST /api/expenses/
GET  /api/expenses/
```

### Summary

```text
GET /api/summary/
```

---

## Authentication

The API uses JWT authentication.

After successful login, the backend returns access and refresh tokens.

The frontend stores the tokens and sends the access token with authenticated API requests.

Example:

```http
Authorization: Bearer <access-token>
```

---

## Create Expense

### Request

```http
POST /api/expenses/
```

### Example Request

```json
{
    "amount": "450.00",
    "category": "Food",
    "note": "Lunch",
    "date": "2026-09-22"
}
```

The authenticated user is automatically associated with the expense.

The client does not provide the user ID.

---

## List Expenses

```http
GET /api/expenses/
```

### Filter by Category

```http
GET /api/expenses/?category=Food
```

### Filter by Date Range

```http
GET /api/expenses/?start_date=2026-09-01&end_date=2026-09-30
```

Category and date filters can also be combined.

---

## Monthly Summary

```http
GET /api/summary/?year=2026&month=9
```

The summary provides:

* Total spending
* Spending by category
* Previous month's total
* Month-over-month percentage change
* Category spending insights above 20%

Example:

```json
{
    "year": 2026,
    "month": 9,
    "total_spend": 6549.0,
    "previous_month_total": 10000.0,
    "month_over_month_change": -35,
    "month_over_month_status": "decreased"
}
```

---

## Validation

The API performs validation including:

* Amount must be greater than `0`
* Category cannot be empty
* Required fields must be provided
* Dates must use `YYYY-MM-DD`
* `start_date` cannot be after `end_date`
* `month` must be between `1` and `12`

Invalid requests return appropriate `400` responses with validation details.

---

## Database

The application uses PostgreSQL.

The main expense model contains:

```text
Expense

- id
- user
- amount
- category
- note
- date
- created_at
- updated_at
```

Each expense is associated with the authenticated user.

This ensures that users can only access their own expense data.

---

# Running Locally

## 1. Clone the Repository

```bash
git clone <repository-url>

cd spend-tracker
```

## 2. Go to the Backend

```bash
cd backend
```

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate on Linux/macOS:

```bash
source venv/bin/activate
```

Activate on Windows:

```cmd
venv\Scripts\activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure Environment Variables

Create a `.env` file inside the `backend` directory.

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=postgres
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
```

Do not commit `.env` to Git.

Use `.env.example` for documenting required environment variables.

## 6. Run Migrations

```bash
python manage.py migrate
```

## 7. Create a Superuser

```bash
python manage.py createsuperuser
```

## 8. Start the Backend

```bash
python manage.py runserver
```

The local API will be available at:

```text
http://127.0.0.1:8000/
```

---

# Frontend

The frontend is built using plain HTML, CSS, and JavaScript.

For local development, start a simple web server from the `frontend` directory:

```bash
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

The frontend communicates with the Django REST API.

For local development, the API base URL is:

```text
http://127.0.0.1:8000/api
```

For production, the frontend uses the deployed Render backend URL.

---

# CORS

Because the frontend and backend are deployed separately, the Django backend must allow requests from the frontend domain.

For example:

```text
Frontend:
https://your-frontend.onrender.com

Backend:
https://your-backend.onrender.com
```

The production frontend URL should be configured in Django's CORS settings.

---

# Running Tests

Run the backend tests using:

```bash
python manage.py test
```

The tests cover:

* Creating an expense
* Invalid expense amount
* Missing category
* Authentication requirement
* Listing expenses
* Category filtering
* Date-range filtering
* User data isolation
* Monthly summary
* Category totals
* Month-over-month calculation
* Category increase greater than 20%

---

# Design Decisions

## Django REST Framework

Django REST Framework was selected because the project is primarily API-based.

DRF provides support for:

* Serializers
* Validation
* Authentication
* Permissions
* API views
* Automated API testing

## PostgreSQL

PostgreSQL is used as the relational database for storing users and expenses.

It provides reliable relational data storage and supports the aggregation queries required for monthly spending summaries.

## Separate Service Logic

Monthly summary calculations are kept in a separate service layer rather than putting all business logic directly inside the API view.

This makes the business logic easier to:

* Test
* Maintain
* Reuse
* Extend

## User-Based Data Isolation

Expenses are associated with the authenticated user.

The API uses the logged-in user when creating and querying expenses instead of accepting a user ID from the client.

This prevents users from requesting another user's expense data through the API.

---

# Deployment

The application is designed to use separate frontend and backend deployments.

### Backend

The Django REST API is deployed on Render.

```text
Backend URL:
<add-render-backend-url-here>
```

### Frontend

The frontend is deployed separately as a Render Static Site.

```text
Frontend URL:
<add-render-frontend-url-here>
```

### Database

The backend connects to PostgreSQL.

```text
Database:
Supabase PostgreSQL
```

Production secrets and database credentials are configured through Render environment variables and are not committed to the repository.

---

# Environment Variables

The following environment variables are required for production:

```text
SECRET_KEY
DEBUG
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

Additional environment variables may be required depending on the production configuration.

---

# What I Would Do With More Time

Potential improvements include:

* Pagination for expenses
* Update expense API
* Delete expense API
* API documentation using OpenAPI/Swagger
* More extensive unit and integration tests
* Improved frontend UX
* CI/CD pipeline
* Production monitoring and logging
* More detailed spending analytics
* Expense charts and visualizations
* Better error and loading states

---

# AI Usage

I used ChatGPT as a coding assistant for project structure, implementation guidance, debugging, and test-case ideas.

I reviewed and tested the generated suggestions and adapted or rejected parts that did not fit the project requirements or implementation.

The final application was tested and integrated into the project by me.

---

# Live Application

### Frontend

https://spend-tracker-frontend-zaau.onrender.com/

### Backend API

https://spend-tracker-backend-7zow.onrender.com/api

### GitHub Repository

https://github.com/madhusudansawant/Spend-Tracker-
