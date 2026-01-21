# Construction Dashboard Deployment Guide

## 🚀 Live Deployment

### Frontend (React + Vercel)
- **URL**: https://frontend-three-zeta-46.vercel.app
- **Status**: ✅ Deployed and running
- **Framework**: React + Vite + Tailwind CSS
- **Features**: Full dashboard UI with charts and KPI displays

### Backend (FastAPI + Vercel Python Runtime)
- **URL**: https://backend-puce-nine.vercel.app
- **Status**: ✅ Deployed and running
- **Framework**: FastAPI + Python 3.9
- **Database**: SQLite (serverless compatible)
- **Features**: REST API with comprehensive construction KPIs

## 🔧 Backend Deployment Options

The backend is now deployed on Vercel using their Python runtime. Alternative deployment options if needed:

### Option 1: Railway (Recommended)
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Deploy the `backend/` directory
4. Set environment variables:
   - `OPENAI_API_KEY` (optional, for AI features)

### Option 2: Render
1. Go to [Render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Heroku
1. Install Heroku CLI
2. Create a `Procfile` in backend directory:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy: `heroku create && git push heroku main`

## 🌐 Connecting Frontend to Backend

The frontend and backend are both deployed on Vercel and are already connected:

- **Frontend**: https://frontend-three-zeta-46.vercel.app
- **Backend API**: https://backend-puce-nine.vercel.app
- **Connection**: Automatic via environment variable `VITE_API_BASE_URL`

### Manual Environment Variable Setup (if needed):
1. In Vercel dashboard → Frontend project settings
2. Add environment variable: `VITE_API_BASE_URL=https://backend-puce-nine.vercel.app`
3. Redeploy the frontend

## 📊 Features Included

### Dashboard Pages
- **Portfolio Overview** - All projects summary
- **Project Detail** - Individual project milestones
- **Billing & Cashflow** - RA bills and receivables
- **Quality & Safety** - NCRs and incidents
- **Railway Blocks** - Block approvals and utilization
- **Job Costing** - Budget vs actual analysis

### KPI Categories (18 Total)
- ✅ Project Progress (SPI, milestones, delays)
- ✅ Cost & Billing (RA bills, CPI, retention)
- ✅ Quality (tests, NCRs, pass rates)
- ✅ Safety (incidents, LTIFR, PPE compliance)
- ✅ Labour & Productivity (manpower, skill mix)
- ✅ Plant & Machinery (utilization, breakdowns)
- ✅ Materials & Supply Chain (lead times, stock)
- ✅ Approvals & Drawings (RFIs, blocks)
- ✅ Contract Compliance (EOT, LD, insurance)
- ✅ Risk Management (risk register, mitigation)

### Technical Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts
- **Backend**: FastAPI, Python, SQLite
- **Deployment**: Vercel (frontend), Railway/Render (backend)
- **AI Integration**: OpenAI API (optional)

## 🔗 Repository
- **GitHub**: https://github.com/amitbharmane-a11y/CSCONSTUCTION-
- **Frontend Live**: https://frontend-three-zeta-46.vercel.app

## 📞 Support
For deployment issues or questions about the construction dashboard, check the comprehensive documentation in the repository.