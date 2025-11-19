# Streamlit Deployment

## Local Testing

```bash
pip install streamlit
cd simulation
streamlit run app.py
```

Visit: http://localhost:8501

## Deploy to Streamlit Cloud (Free)

1. **Push to GitHub**

2. **Go to**: https://share.streamlit.io

3. **Connect Repository**:
   - Select: `YOUR_USERNAME/Ethic-Latex`
   - Main file path: `simulation/app.py`
   - Python version: 3.10

4. **Deploy**

Your app will be available at:
```
https://YOUR_APP_NAME.streamlit.app
```

## Deploy to Heroku

See `deploy/heroku/README.md`

## Deploy to Docker

```bash
docker build -t erh-app .
docker run -p 8501:8501 erh-app streamlit run simulation/app.py --server.port=8501 --server.address=0.0.0.0
```

