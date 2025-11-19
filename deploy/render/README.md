# Render Deployment

## Steps

1. **Sign up**: https://render.com

2. **New Web Service**

3. **Connect GitHub** repository

4. **Configure**:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run simulation/app.py --server.port=$PORT --server.address=0.0.0.0`

5. **Deploy**

## Free Tier

- 750 hours/month
- Spins down after 15 min inactivity
- Public URL provided

