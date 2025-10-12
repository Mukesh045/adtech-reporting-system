# Adtech Reporting System

A full-stack web application for processing, storing, and visualizing adtech reporting data from CSV files with 200k+ records. Built for programmatic advertising analytics, featuring data import, dashboard summaries, dynamic report building, and export capabilities.

## Overview

This application allows users to:
- Upload and import CSV adtech data into MongoDB.
- View high-level dashboard metrics (total requests, impressions, clicks, payout, eCPM).
- Build custom reports with selectable dimensions/metrics, date ranges, filters, search, and saved configurations.
- Export reports as CSV.

It handles large datasets efficiently with MongoDB aggregation pipelines and React optimizations.

## Project Structure

```
adreport/
├── backend/                    # FastAPI backend
│   ├── main.py                 # App entry point and middleware
│   ├── routers/                # API route definitions
│   │   ├── data.py             # Data import endpoints (POST /api/data/import, GET /api/data/import/{job_id})
│   │   └── reports.py          # Reporting endpoints (query, export, summary, saved reports)
│   ├── models.py               # Pydantic models for requests/responses and MongoDB schemas
│   └── database.py             # MongoDB connection and utilities
├── src/                        # React frontend
│   ├── components/             # Reusable UI components
│   │   ├── Reports.tsx         # Dynamic report builder, table, charts, save/load
│   │   ├── Dashboard.tsx       # Summary statistics cards
│   │   ├── DataImport.tsx      # CSV upload with progress tracking
│   │   └── ErrorBoundary.tsx   # Global error handling
│   ├── App.tsx                 # Main layout with sider menu and routing
│   ├── App.css                 # Global styles and Ant Design overrides
│   └── types.ts                # TypeScript interfaces (e.g., ReportQueryRequest, DashboardData)
├── requirements.txt            # Python dependencies (fastapi, uvicorn, pymongo, pandas)
├── package.json                # NPM dependencies (react, antd, recharts, axios)
├── README.md                   # Project documentation
├── test_api.py                 # Integration tests for all APIs
├── .env.example                # Template for environment variables
├── setupback.bat               # Windows setup script (optional) # to setup backend
└── startback.bat               # Windows start script (optional) # to start backend
```

## Tech Stack

- **Backend**: Python 3.10+ with FastAPI (RESTful APIs, async support).
- **Database**: MongoDB (via PyMongo for bulk inserts and aggregations).
- **Frontend**: React 18+ with TypeScript, Ant Design (UI components), Recharts (visualizations), Axios (API calls).
- **Other**: Pandas (CSV processing), Celery (optional background jobs for imports), NPM/Yarn for frontend.
- **Testing**: Pytest (backend), Jest (frontend), test_api.py (API integration tests).
- **Deployment**: Railway (backend), Vercel (frontend), MongoDB Atlas (database).

## Local Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and NPM/Yarn
- MongoDB (local or Atlas cluster)
- Git

### 1. Clone the Repository
```
git clone <your-repo-url>
cd adreport
```

### 2. Backend Setup
```
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
MONGODB_URI=mongodb://localhost:27017/adreport  # Or your Atlas URI
SECRET_KEY=your-secret-key  # For any auth if added
```

### 3. Database Setup
- **Local MongoDB**: Install MongoDB Community Edition and start the service (`mongod`).
- **MongoDB Atlas**: Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com), get the connection string, and update `MONGODB_URI` in .env. Whitelist your IP.

No schema migrations needed (MongoDB is schemaless). Collections: `ad_reports`, `saved_reports`, `import_jobs`.

### 4. Frontend Setup
```
cd adreport  # If not already in root

# Install dependencies
npm install  # Or yarn install

# Set environment variables (in .env or via npm)
REACT_APP_API_URL=http://localhost:8000  # Backend URL
```

### 5. Running the Application

#### Backend
```
# From root directory
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- API docs: http://localhost:8000/docs (Swagger UI).
- Test APIs: Run `python test_api.py` for integration tests.

#### Frontend
```
# In a new terminal, from root
npm start
```
- App runs at http://localhost:3000.

#### Full Stack
1. Start MongoDB.
2. Run backend (uvicorn).
3. Run frontend (npm start).
4. Open http://localhost:3000 in browser.
5. Upload sample CSV via Data Import page to test.

### Sample Data
Use the provided CSV structure (dimensions: date, mobile_app_resolved_id, etc.; metrics: ad_exchange_total_requests, payout, etc.). For testing, use the sample in `test_api.py` or download a 200k+ record CSV matching the schema.

## API Documentation

All endpoints under `/api`. Use Swagger at `/docs` for interactive testing.

### Postman Collection
For easier API testing with examples, import the collection from `adreport/adreport.postman_collection.json` into Postman. It includes all endpoints with pre-configured requests, example bodies, and expected responses. Set the `base_url` variable to your backend URL (e.g., http://localhost:8000 for local development).

### Data Import
- **POST /api/data/import**: Upload CSV. Multipart/form-data, field: `file`.
  - Example Request: Upload a CSV file via form-data.
  - Example Response: `{ "job_id": "550e8400-e29b-41d4-a716-446655440000" }`.
- **GET /api/data/import/{job_id}**: Poll status.
  - Example Request: `GET /api/data/import/550e8400-e29b-41d4-a716-446655440000`
  - Example Response: `{ "status": "completed", "progress": 100, "processed_records": 200000, "total_records": 200000, "errors": [] }`.

### Reports
- **GET /api/reports/dimensions**: Returns list of available dimensions.
  - Example Response: `["date", "mobile_app_name", "mobile_app_resolved_id", "ad_exchange_name", "country_code", "device_type"]`.
- **GET /api/reports/metrics**: Returns list of available metrics.
  - Example Response: `["ad_exchange_total_requests", "ad_exchange_total_impressions", "ad_exchange_total_clicks", "payout", "ecpm"]`.
- **POST /api/reports/query**: Dynamic query.
  - Example Request Body: `{ "dimensions": ["date", "mobile_app_name"], "metrics": ["ad_exchange_total_requests", "payout"], "filters": { "country_code": ["US", "IN"] }, "date_range": { "start": "2023-01-01", "end": "2023-12-31" }, "page": 1, "limit": 100 }`.
  - Example Response: `{ "data": [{ "date": "2023-01-01", "mobile_app_name": "App1", "ad_exchange_total_requests": 10000, "payout": 500.0 }], "total": 500, "page": 1 }`.
- **POST /api/reports/export**: Export to CSV.
  - Example Request Body: Same as query, but `limit` up to 10000.
  - Example Response: CSV stream like `date,payout\n2023-01-01,500.0\n2023-01-02,450.0`.

### Dashboard
- **GET /api/reports/summary**: Aggregated metrics.
  - Example Response: `{ "ad_exchange_total_requests": 1000000, "ad_exchange_total_impressions": 800000, "ad_exchange_total_clicks": 50000, "payout": 25000.0, "average_ecpm": 2.5 }`.

### Saved Reports
- **POST /api/reports/saved-reports**: Save config.
  - Example Request Body: `{ "name": "My Custom Report", "dimensions": ["date", "mobile_app_name"], "metrics": ["ad_exchange_total_requests", "payout"], "date_range": { "start": "2023-01-01", "end": "2023-12-31" } }`.
  - Example Response: `{ "id": "550e8400-e29b-41d4-a716-446655440001", "message": "Saved" }`.
- **GET /api/reports/saved-reports**: List all.
  - Example Response: `[{ "id": "550e8400-e29b-41d4-a716-446655440001", "name": "My Custom Report", "dimensions": ["date", "mobile_app_name"], "metrics": ["ad_exchange_total_requests", "payout"], "date_range": { "start": "2023-01-01", "end": "2023-12-31" }, "created_at": "2023-10-01T12:00:00Z" }]`.
- **DELETE /api/reports/saved-reports/{id}**: Delete.
  - Example Request: `DELETE /api/reports/saved-reports/550e8400-e29b-41d4-a716-446655440001`
  - Example Response: `{ "message": "Deleted" }`.

### Other
- **GET /api/reports/latest_report_id**: Get latest report ID.
  - Example Response: `{ "report_id": "report-2" }`.
- **GET /api/reports/report_ids**: Get list of report IDs.
  - Example Response: `{ "report_ids": ["report-1", "report-2"] }`.

Error responses: JSON `{ "detail": "Error message" }` with HTTP 4xx/5xx.

## Deployment Guide

### Backend Deployment (Railway)
1. **Push Code to GitHub**: Ensure all code is committed and pushed to a GitHub repository.
2. **Create Railway Account**: Sign up at [railway.app](https://railway.app) using GitHub or email.
3. **Create New Project**: Click "New Project" > "Deploy from GitHub repo" > Select your repo > Click "Deploy".
4. **Configure Environment Variables**:
   - Go to your project dashboard > Variables tab.
   - Add: `MONGODB_URI` (your Atlas connection string), `PORT=8000`.
   - Optionally add `SECRET_KEY` for any auth.
5. **Deploy**: Railway auto-detects Python/FastAPI and runs `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
6. **Get Backend URL**: After deployment, note the generated URL (e.g., https://your-app.railway.app).
7. **Update CORS**: In `backend/main.py`, update `allow_origins` to include your frontend URL (e.g., `["https://your-frontend.vercel.app"]`).
8. **Verify API Docs**: Access https://your-app.railway.app/docs for Swagger UI.


### Database Setup (MongoDB Atlas)
1. **Create Account**: Sign up at [cloud.mongodb.com](https://cloud.mongodb.com).
2. **Create Cluster**: Choose a free M0 cluster > Select region > Create cluster (takes ~5-10 mins).
3. **Create Database**: Go to Collections > Create Database named `adreport`.
4. **Get Connection String**: Clusters > Connect > Connect your application > Copy the string: `mongodb+srv://user:pass@cluster.mongodb.net/adreport?retryWrites=true&w=majority`.
5. **Whitelist IPs**: Network Access > Add IP Address > Allow Access from Anywhere (0.0.0.0/0) for development.
6. **Add to Backend Env Vars**: Paste the connection string as `MONGODB_URI` in Railway variables.


### Frontend Deployment (Vercel)
1. **Push Code to GitHub**: Ensure frontend code is in the repo (e.g., in `adreport/` or root).
2. **Create Vercel Account**: Sign up at [vercel.com](https://vercel.com) using GitHub.
3. **Import Project**: Dashboard > "New Project" > Import GitHub repo > Select your repo.
4. **Configure Build Settings** (if needed):
   - Root Directory: `adreport` (if frontend is in subfolder).
   - Build Command: `npm run build` or `yarn build`.
   - Output Directory: `build`.
5. **Add Environment Variables**:
   - Go to Project Settings > Environment Variables.
   - Add: `REACT_APP_API_URL=https://your-backend.railway.app`.
6. **Deploy**: Vercel auto-builds React and deploys to a static site.
7. **Get Frontend URL**: Note the generated URL (e.g., https://your-app.vercel.app).

### Full Deployment Steps
1. **Deploy Database**: Set up MongoDB Atlas cluster and database.
2. **Deploy Backend**: Deploy to Railway, connect to Atlas via env vars, update CORS for frontend URL.
3. **Deploy Frontend**: Deploy to Vercel, set `REACT_APP_API_URL` to Railway URL.
4. **Test Deployment**:
   - Upload CSV via frontend Data Import page.
   - Verify dashboard loads summary metrics.
   - Test report building, filtering, and export.
   - Check API docs at backend URL/docs.
5. **Monitor and Troubleshoot**:
   - Check Railway/Vercel logs for errors.
   - Ensure CORS is configured correctly.
   - Verify database connections.

Costs: Free tiers available (Railway: $5/month credit, Vercel: generous free plan, Atlas: 512MB free cluster).

## Testing

- **API Tests**: `python test_api.py` (runs all endpoints with samples).
- **Backend Unit**: `pytest backend/` (add tests for routers/models).
- **Frontend Unit**: `npm test` (Jest for components).
- **E2E**: Manual via browser or Cypress (add if needed).
- **Load Test**: Use Locust for 200k+ data imports.

## Performance Notes
- Backend: Aggregation pipelines optimized for grouping/summing on 200k+ records (<5s queries).
- Frontend: Pagination/virtual scrolling in Table for large results; debounced search (300ms delay) to improve performance; charts limited to 20 items.
- Import: Background jobs prevent blocking; handles 200k CSV in ~30s.

## Troubleshooting
- **CORS Errors**: Check origins in main.py.
- **DB Connection**: Verify MONGODB_URI, whitelist IPs.
- **Import Fails**: Ensure CSV headers match schema; check job status.
- **TS Errors**: Run `npm run build` to check.
- **Large CSV**: Increase timeout in requests/axios.

## Contributing
Fork, PR with tests. Follow PEP8 for Python, ESLint for TS.

## Contact me
For questions, contact [msingh782004@gmail.com].
