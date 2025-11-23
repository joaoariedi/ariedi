# Ariedi Portfolio

Personal portfolio website showcasing projects, workshops, and professional experience as an Engineering Leader & Cybersecurity Expert.

## Tech Stack

- **Framework:** Django 5.2
- **Database:** PostgreSQL (Heroku) / SQLite (local)
- **Storage:** AWS S3 (media files)
- **Deployment:** Heroku
- **Package Manager:** Poetry

## Project Structure

```
ariedi-v2/
├── core/           # Django project settings and configuration
├── pages/          # Main pages and contact form
├── projects/       # Portfolio projects management
├── category/       # Project categorization
├── workshops/      # Workshops and events
├── templates/      # HTML templates
├── static/         # Static assets
└── staticfiles/    # Collected static files
```

## Local Development

### Prerequisites

- Python 3.12+
- Poetry

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ariedi-v2.git
cd ariedi-v2
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file with required variables:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
```

4. Run migrations:
```bash
poetry run python manage.py migrate
```

5. Start the development server:
```bash
poetry run python manage.py runserver
```

Visit `http://localhost:8000`

## Deployment (Heroku)

This project uses Heroku's native Poetry support (no third-party buildpacks required).

### Required Files

- `pyproject.toml` - Poetry configuration
- `poetry.lock` - Locked dependencies
- `.python-version` - Python version (3.12)
- `Procfile` - Heroku process configuration

### Environment Variables

Set these in Heroku dashboard or CLI:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Set to `False` in production |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for S3 |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name |
| `MAILGUN_SMTP_*` | Email configuration (optional) |

### Deploy

```bash
git push heroku main
```

Heroku will automatically:
1. Detect Poetry from `pyproject.toml` + `poetry.lock`
2. Install dependencies via Poetry
3. Run `collectstatic`
4. Start the gunicorn server

## License

All rights reserved.
