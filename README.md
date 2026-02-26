# NC100BW Training Portal
### Pure Python + Django + PostgreSQL + HTML

No React. No Node.js. No npm. Just Python.

---

## Setup (one time)

### 1. PostgreSQL — create the database

Open pgAdmin or Command Prompt as Admin:

```sql
psql -U postgres

CREATE DATABASE ncbw_training;
CREATE USER ncbw_user WITH PASSWORD 'ncbw_password123';
GRANT ALL PRIVILEGES ON DATABASE ncbw_training TO ncbw_user;
\q
```

### 2. Install Python packages

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Set up database & create admin

```bash
python manage.py migrate
python manage.py create_admin
```

---

## Run the app

```bash
python manage.py runserver
```

Open: **http://localhost:8000**

Login: `admin@nc100bw.org` / `Admin@1234`

---

## Project Files (all Python or HTML)

```
ncbw-final/
├── manage.py                   ← run commands here
├── requirements.txt            ← django + psycopg2
├── config/
│   ├── settings.py             ← database config
│   └── urls.py
└── ncbw/
    ├── models.py               ← User, Progress tables
    ├── views.py                ← all page logic
    ├── urls.py                 ← page routes
    ├── training_data.py        ← all course content
    ├── management/commands/
    │   └── create_admin.py
    └── templates/ncbw/
        ├── base.html           ← shared layout & styles
        ├── login.html
        ├── signup.html
        ├── select_track.html
        ├── dashboard.html
        ├── module.html         ← courses + quiz
        └── admin.html          ← admin dashboard
```

---

## Change database password

Edit `config/settings.py`:

```python
DATABASES = {
    'default': {
        'NAME': 'ncbw_training',
        'USER': 'ncbw_user',
        'PASSWORD': 'your_new_password',  # ← here
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
