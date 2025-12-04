# Deploying AI Travel Planner to Render

This guide walks you through deploying the AI Travel Planner to Render with a static frontend and Dockerized backend.

## 📋 Prerequisites

- GitHub account with your code pushed
- Render account (free tier works)
- API keys ready:
  - `GEMINI_API_KEY` (for Google Gemini LLM)
  - `GEOAPIFY_API_KEY` (for location services)
  - `OPEN_WEATHER_API_KEY` (for weather data)
  - `OPENAI_API_KEY` (optional, if using OpenAI models)

## 🚀 Deployment Steps

### Step 1: Deploy Backend (Docker Web Service)

1. **Create New Web Service**
   - Log in to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `ai-trip-planner-backend` (or your choice)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Plan**: Free (or paid for better performance)

3. **Add Environment Variables**
   Click "Advanced" and add these environment variables:
   
   | Key | Value | Notes |
   |-----|-------|-------|
   | `GEMINI_API_KEY` | `your_actual_gemini_key` | Required - Get from Google AI Studio |
   | `GEOAPIFY_API_KEY` | `your_geoapify_key` | Required - Get from Geoapify dashboard |
   | `OPEN_WEATHER_API_KEY` | `your_openweather_key` | Required - Get from OpenWeatherMap |
   | `OPENAI_API_KEY` | `your_openai_key` | Optional - Only if using OpenAI models |
   | `ALLOWED_ORIGINS` | `https://ai-trip-planner-frontend.onrender.com` | Update with your frontend URL after Step 2 |

   > **Important**: Replace `ai-trip-planner-frontend.onrender.com` with your actual frontend URL once deployed

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes for first build)
   - Note your backend URL: `https://your-backend-name.onrender.com`

5. **Verify Backend**
   - Visit: `https://your-backend-name.onrender.com/api/health`
   - Should return: `{"status":"healthy","agent_ready":true}`

---

### Step 2: Deploy Frontend (Static Site)

1. **Create Static Site**
   - In Render Dashboard, click "New +" → "Static Site"
   - Connect the same GitHub repository

2. **Configure Site**
   - **Name**: `ai-trip-planner-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

3. **Add Environment Variables**
   Click "Advanced" and add:
   
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://your-backend-name.onrender.com` |

   > Replace with your actual backend URL from Step 1

4. **Deploy**
   - Click "Create Static Site"
   - Wait for build and deployment (3-5 minutes)
   - Note your frontend URL: `https://ai-trip-planner-frontend.onrender.com`

---

### Step 3: Update CORS Settings

After both services are deployed, update the backend CORS configuration:

1. Go to your backend service in Render
2. Navigate to "Environment" tab
3. Update `ALLOWED_ORIGINS` variable:
   ```
   https://your-actual-frontend-url.onrender.com
   ```
4. Save changes - backend will automatically redeploy

---

## ✅ Verification

1. **Test Health Endpoint**
   ```bash
   curl https://your-backend-name.onrender.com/api/health
   ```

2. **Open Frontend**
   - Visit your frontend URL
   - You should see the VoyageIQ interface

3. **Test Chat**
   - Enter a message like "What's the weather in Paris?"
   - You should see streaming responses and thinking steps

4. **Check Browser Console**
   - Open Developer Tools (F12)
   - Verify no CORS errors
   - Check network tab for successful API calls

---

## 🔧 Troubleshooting

### Backend Issues

**Problem**: Health check fails
- **Check**: Environment variables are set correctly
- **Check**: `GEMINI_API_KEY` is valid
- **Solution**: View logs in Render dashboard

**Problem**: "Agent not initialized" error
- **Check**: Backend logs for startup errors
- **Solution**: Verify API keys are correct

### Frontend Issues

**Problem**: Can't connect to backend
- **Check**: `VITE_API_URL` environment variable is set
- **Check**: Backend health endpoint responds
- **Solution**: Verify CORS settings in backend

**Problem**: CORS errors in browser console
- **Check**: `ALLOWED_ORIGINS` includes your frontend URL
- **Solution**: Update backend environment variable

### Performance Issues

**Problem**: Slow cold starts (Free tier)
- **Explanation**: Free tier services sleep after 15 min of inactivity
- **Solution**: Upgrade to paid tier or accept cold start delay

---

## 💡 Tips

1. **Development vs Production**
   - Local dev uses Vite proxy (no CORS issues)
   - Production requires CORS configuration

2. **Environment Variables**
   - Never commit `.env` files with real API keys
   - Always use Render's environment variable dashboard

3. **Monitoring**
   - Check Render logs regularly
   - Set up log persistence on paid plans

4. **Updates**
   - Push to GitHub triggers auto-deployment
   - Manual deploys available in Render dashboard

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Docker Deployment Guide](https://render.com/docs/docker)
- [Static Sites on Render](https://render.com/docs/static-sites)
- [Environment Variables](https://render.com/docs/environment-variables)

---

## 🔐 Security Notes

- Never expose API keys in frontend code
- Use environment variables for all secrets
- Restrict CORS origins in production
- Consider adding rate limiting for production use
