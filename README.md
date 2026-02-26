# NCBW Training Portal — Django + PostgreSQL Backend

---

## Step 1 — Set Up PostgreSQL

Open pgAdmin or run in Command Prompt (as Admin):

```sql
psql -U postgres

CREATE DATABASE ncbw_training;
CREATE USER ncbw_user WITH PASSWORD 'ncbw_password123';
GRANT ALL PRIVILEGES ON DATABASE ncbw_training TO ncbw_user;
\q
```

---

## Step 2 — Run the Backend

Open a terminal in VS Code, go to the `backend` folder:

```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate it — Windows:
venv\Scripts\activate

# Install packages (first time only)
pip install -r requirements.txt

# Set up database tables
python manage.py migrate

# Create default admin account
python manage.py create_admin

# Start the server
python manage.py runserver
```

Backend runs at: **http://localhost:8000**

---

## Step 3 — Run the Frontend

Open a **second terminal**, go to the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## Default Login

| Email                 | Password   | Role  |
|-----------------------|------------|-------|
| admin@nc100bw.org     | Admin@1234 | Admin |

---

## Project Structure

```
ncbw-project/
├── backend/
│   ├── manage.py              ← Run Django commands here
│   ├── requirements.txt       ← Python packages
│   ├── backend/
│   │   ├── settings.py        ← Database config here
│   │   └── urls.py
│   └── api/
│       ├── models.py          ← Database tables (User, Session, Progress)
│       ├── views.py           ← All API logic
│       └── urls.py            ← API routes
│
└── frontend/
    └── src/
        └── utils/api.ts       ← Calls Django backend
```

---

## If you change the database password

Edit `backend/backend/settings.py`:

```python
DATABASES = {
    'default': {
        'NAME': 'ncbw_training',
        'USER': 'ncbw_user',
        'PASSWORD': 'your_new_password',   # ← change here
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
