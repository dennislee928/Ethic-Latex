# Heroku Deployment

## Prerequisites

1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Create Heroku account: https://www.heroku.com

## Quick Deploy

### Method 1: Using Heroku CLI

```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

### Method 2: Using GitHub Integration

1. Connect GitHub repo in Heroku dashboard
2. Enable automatic deploys
3. Manual deploy from main branch

## Configuration

Create `Procfile`:
```
web: streamlit run simulation/app.py --server.port=$PORT --server.address=0.0.0.0
```

Create `runtime.txt`:
```
python-3.10.12
```

## Environment Variables

Set in Heroku dashboard or CLI:
```bash
heroku config:set PYTHONUNBUFFERED=1
```

## Access

Your app will be at:
```
https://your-app-name.herokuapp.com
```

