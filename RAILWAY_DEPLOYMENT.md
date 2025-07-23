# Railway Deployment Guide

This guide will help you deploy the Loan Application Backend to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. Railway CLI installed (optional but recommended)

## Deployment Steps

### Method 1: Using Railway Dashboard (Recommended)

1. **Create a New Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account and select this repository

2. **Add Required Services**
   - In your Railway project dashboard, click "+ New"
   - Add a **PostgreSQL** database service
   - Add a **Redis** service

3. **Configure Environment Variables**
   - Go to your main service settings
   - Add the following environment variables:
     ```
     JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
     ENVIRONMENT=production
     DEBUG=false
     LOG_LEVEL=info
     ```
   - Railway will automatically provide:
     - `DATABASE_URL` (from PostgreSQL service)
     - `REDIS_URL` (from Redis service)
     - `PORT` (Railway's assigned port)

4. **Deploy**
   - Railway will automatically deploy your application
   - The deployment will use the `railway.toml` configuration

### Method 2: Using Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Add Services**
   ```bash
   railway add postgresql
   railway add redis
   ```

5. **Set Environment Variables**
   ```bash
   railway variables set JWT_SECRET_KEY=your-super-secret-jwt-key
   railway variables set ENVIRONMENT=production
   railway variables set DEBUG=false
   ```

6. **Deploy**
   ```bash
   railway up
   ```

## Important Notes

### Security
- **Always change the JWT_SECRET_KEY** to a secure random string in production
- Never commit sensitive environment variables to your repository
- Use Railway's environment variable management for secrets

### Database Setup
- Railway will automatically create the PostgreSQL database
- You may need to run database migrations after deployment
- Consider adding a startup script to handle database initialization

### File Uploads
- The current configuration uses local file storage (`./uploads`)
- For production, consider using Railway's persistent volumes or external storage (AWS S3, etc.)

### Monitoring
- Railway provides built-in monitoring and logs
- Access logs through the Railway dashboard
- Set up alerts for critical errors

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL service is running
   - Check if DATABASE_URL is properly set
   - Verify database credentials

2. **Redis Connection Errors**
   - Ensure Redis service is running
   - Check if REDIS_URL is properly set

3. **Port Binding Issues**
   - Railway automatically sets the PORT environment variable
   - The application is configured to use `0.0.0.0:$PORT`

4. **Environment Variable Issues**
   - Double-check all required environment variables are set
   - Ensure no typos in variable names

### Getting Help

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Community: [Railway Discord](https://discord.gg/railway)
- Check Railway status: [status.railway.app](https://status.railway.app)

## Post-Deployment

1. **Test the API**
   - Visit your Railway app URL
   - Test the health check endpoint: `GET /api/health`
   - Verify database connectivity

2. **Set up Domain (Optional)**
   - Configure a custom domain in Railway dashboard
   - Update any frontend applications with the new API URL

3. **Monitor Performance**
   - Use Railway's built-in metrics
   - Set up external monitoring if needed
   - Configure log aggregation for better debugging

Your FastAPI application should now be successfully deployed on Railway!