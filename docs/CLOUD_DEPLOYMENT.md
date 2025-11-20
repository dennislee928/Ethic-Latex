# Cloud Deployment Guide - Quick Reference

## 🚀 Recommended Options (Easiest to Hardest)

### 1. **Binder** (Free, No Setup) ⭐ Easiest
**Best for**: Sharing notebooks publicly

```bash
# Just push to GitHub, then visit:
https://mybinder.org/v2/gh/YOUR_USERNAME/Ethic-Latex/main
```

**Pros**: 
- Completely free
- Zero configuration
- Public access
- JupyterLab interface

**Cons**: 
- Sessions timeout after inactivity
- No persistent storage

---

### 2. **Streamlit Cloud** (Free, Easy) ⭐⭐ Recommended
**Best for**: Interactive web application

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect repo → Deploy
4. Done!

**URL**: `https://your-app.streamlit.app`

**Pros**:
- Free tier available
- Automatic HTTPS
- Easy deployment
- Great for demos

**Cons**:
- Limited to Streamlit apps
- Resource limits on free tier

---

### 3. **Railway** (Easy, Paid) ⭐⭐⭐
**Best for**: Full control, persistent apps

1. Sign up at https://railway.app
2. Deploy from GitHub
3. Configure start command
4. Deploy

**Pros**:
- Very easy setup
- Persistent storage
- Custom domains
- Good free tier

**Cons**:
- Limited free tier
- Paid plans for production

---

### 4. **Render** (Free Tier Available)
**Best for**: Simple web apps

Similar to Railway, with free tier that spins down after inactivity.

---

### 5. **Docker + Any Cloud** (Most Flexible)
**Best for**: Production deployments

Deploy the Docker container to:
- AWS ECS/EC2
- Google Cloud Run
- Azure Container Instances
- DigitalOcean
- Any Docker host

---

## Quick Comparison

| Platform | Free Tier | Setup Time | Best For |
|----------|-----------|------------|----------|
| Binder | ✅ Yes | 0 min | Notebooks |
| Streamlit Cloud | ✅ Yes | 5 min | Web apps |
| Railway | ✅ Limited | 10 min | Full apps |
| Render | ✅ Yes | 10 min | Web apps |
| Heroku | ❌ No | 15 min | Web apps |
| AWS EC2 | ✅ 12 months | 30 min | Production |
| Docker | Varies | 20 min | Flexibility |

---

## Step-by-Step: Streamlit Cloud (Recommended)

### 1. Ensure `simulation/app.py` exists
✅ Already created!

### 2. Add to `requirements.txt`:
```
streamlit>=1.28.0
```

### 3. Push to GitHub:
```bash
git add .
git commit -m "Add Streamlit app"
git push
```

### 4. Deploy:
1. Visit https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `YOUR_USERNAME/Ethic-Latex`
5. Main file path: `simulation/app.py`
6. Click "Deploy"

### 5. Access:
Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## Step-by-Step: Binder (For Notebooks)

### 1. Ensure `binder/environment.yml` exists
✅ Already created!

### 2. Push to GitHub:
```bash
git add binder/
git commit -m "Add Binder support"
git push
```

### 3. Get Binder URL:
```
https://mybinder.org/v2/gh/YOUR_USERNAME/Ethic-Latex/main
```

### 4. Share the URL:
Anyone can click and get a live JupyterLab session!

---

## Step-by-Step: Railway (Full App)

### 1. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run simulation/app.py --server.port=$PORT --server.address=0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. Push to GitHub

### 3. Deploy on Railway:
1. New Project → GitHub Repo
2. Auto-detects configuration
3. Deploy!

---

## Security Considerations

### For Public Access:

1. **Authentication**:
   - Streamlit: Built-in password protection
   - Jupyter: Use tokens or passwords
   - Add authentication middleware

2. **HTTPS**:
   - Most platforms provide automatically
   - For self-hosted: Use nginx + Let's Encrypt

3. **Rate Limiting**:
   - Implement in application code
   - Use platform features

4. **Resource Limits**:
   - Set memory/CPU limits
   - Monitor usage

---

## Environment Variables

Set these in your cloud platform:

```bash
PYTHONUNBUFFERED=1
JUPYTER_ENABLE_LAB=yes
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## Monitoring

### Add Health Check Endpoint

For `simulation/app.py`:
```python
# Add health check route
if st.button("Health Check"):
    st.success("System operational!")
```

### Logging

Most platforms provide:
- Application logs
- Error tracking
- Performance metrics

---

## Cost Estimates

### Free Tiers:
- **Binder**: Completely free
- **Streamlit Cloud**: Free (with limits)
- **Render**: Free (spins down)
- **Railway**: $5 credit/month

### Paid Options:
- **Railway Hobby**: $5/month
- **AWS EC2 t3.micro**: ~$7/month
- **DigitalOcean Droplet**: $6/month
- **Heroku**: $7/month (Basic)

---

## Troubleshooting

### Common Issues:

1. **Port binding errors**:
   - Use `0.0.0.0` not `localhost`
   - Use `$PORT` environment variable

2. **Import errors**:
   - Ensure all dependencies in `requirements.txt`
   - Check Python path in app

3. **Memory issues**:
   - Reduce `num_actions` in app
   - Upgrade instance size

4. **Timeout errors**:
   - Optimize code
   - Use background tasks for long operations

---

## Next Steps

1. **Choose a platform** based on your needs
2. **Test locally** first:
   ```bash
   streamlit run simulation/app.py
   ```
3. **Deploy** following platform-specific guide
4. **Monitor** and iterate

---

## Support

- **Binder**: https://mybinder.readthedocs.io
- **Streamlit**: https://docs.streamlit.io
- **Railway**: https://docs.railway.app
- **Docker**: https://docs.docker.com

