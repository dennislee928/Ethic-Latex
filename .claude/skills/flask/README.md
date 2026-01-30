# Flask Skill

**Status**: Production Ready
**Last Updated**: December 2025

## Auto-Trigger Keywords

### Primary
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask blueprints

### Secondary
- Python web app
- Jinja templates
- Flask factory pattern
- WSGI
- Werkzeug
- Flask-WTF

### Error-Based
- "circular import"
- "Working outside of application context"
- "cannot import name"
- "CSRF token is missing"
- "Could not build url for endpoint"

## What This Skill Does

Provides production-tested patterns for building Flask web applications:

- **Project Setup**: uv-based initialization
- **Structure**: Application factory pattern
- **Blueprints**: Modular route organization
- **Database**: Flask-SQLAlchemy integration
- **Authentication**: Flask-Login with forms
- **API Routes**: JSON endpoints
- **Testing**: pytest fixtures
- **Deployment**: Gunicorn patterns

## Known Issues Prevented

| Issue | Symptom | Prevention |
|-------|---------|------------|
| Circular imports | "cannot import name" | Extensions in separate file |
| Application context | "Working outside of application context" | Factory pattern + app_context |
| Blueprint routing | "Could not build url" | Correct url_for("blueprint.route") |
| CSRF errors | "CSRF token missing" | form.hidden_tag() in templates |
| Import order | Partial module init | Import routes at bottom of __init__.py |

## When to Use

- Creating Flask web applications
- Building traditional server-rendered apps
- Projects requiring Jinja templates
- Simple to medium complexity APIs
- When you prefer Flask over FastAPI

## When NOT to Use

- High-performance async APIs (use FastAPI)
- Already using FastAPI
- Microservices (consider FastAPI)
- Real-time applications (consider WebSockets frameworks)

## Version Info

| Package | Version |
|---------|---------|
| Flask | 3.1.2 |
| Flask-SQLAlchemy | 3.1.1 |
| Flask-Login | 0.6.3 |
| Flask-WTF | 1.2.2 |
| Werkzeug | 3.1.3 |

## Quick Start

```bash
uv init my-flask-app && cd my-flask-app
uv add flask flask-sqlalchemy flask-login flask-wtf python-dotenv
uv run flask --app app run --debug
```

## Resources

- `SKILL.md` - Full documentation
- `templates/` - Ready-to-use project files
