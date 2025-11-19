# Railway Deployment (Easiest Cloud Option)

Railway is one of the easiest platforms for deploying Python apps.

## Steps

1. **Sign up**: https://railway.app

2. **New Project** → Deploy from GitHub

3. **Select Repository**: `YOUR_USERNAME/Ethic-Latex`

4. **Configure**:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run simulation/app.py --server.port=$PORT --server.address=0.0.0.0`

5. **Deploy**

Your app will be live at: `https://your-app.railway.app`

## Environment Variables

Set in Railway dashboard if needed.

## Pricing

- Free tier: $5 credit/month
- Hobby: $5/month
- Pro: $20/month

