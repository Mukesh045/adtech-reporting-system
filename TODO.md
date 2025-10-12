- [x] Create adreport/backend/__init__.py
- [x] Create adreport/backend/routers/__init__.py
- [x] Edit adreport/backend/main.py to change import to relative
- [x] Test by running startback.bat (fixed import error)

## Making UI Responsive for Mobile, Tablet, etc.

- [x] Step 1: Update App.tsx to add collapsible Sider and responsive layout.
- [x] Step 2: Add media queries to App.css for font sizes and element adjustments on smaller screens.
- [x] Step 3: Modify Dashboard.tsx to use responsive grid (e.g., Col xs={24} sm={12} md={6}).
- [x] Step 4: Ensure DataImport.tsx Dragger and Cards are full-width on mobile.
- [x] Step 5: Update Reports.tsx for responsive Selects, Buttons, scrollable Table, and flexible Chart.
- [x] Step 6: Add global responsive styles to index.css if necessary.
- [x] Step 7: Verify responsiveness using browser dev tools or local run.

## Backend Deployment Fix on Railway

- [x] Update CORS origins in backend/main.py to include Vercel frontend URL
- [x] Add global db_connected flag in backend/main.py
- [x] Modify startup event in backend/main.py to set db_connected flag on success
- [x] Add /health GET endpoint in backend/main.py
- [x] Commit changes: git add backend/main.py && git commit -m "Update CORS for Vercel and add /health endpoint"
- [x] Push to Git to trigger Railway redeploy
- [x] Verify deploy logs in Railway dashboard for successful startup
- [x] Add logging to backend/main.py for debugging startup and router loading
- [x] Commit and push logging changes
- [x] Check Railway logs for logging output (e.g., "Including reports router")
- [x] Update Procfile to add --log-level debug for uvicorn to capture tracebacks
- [x] Commit and push Procfile change
- [x] Fix Dockerfile CMD to use backend.main:app module path
- [x] Commit and push Dockerfile change
- [x] Fix Dockerfile CMD to use sh -c for $PORT expansion
- [x] Commit and push Dockerfile change for shell expansion
- [x] Remove Dockerfile to rely on Procfile for proper $PORT expansion
- [x] Commit and push removal of Dockerfile
- [x] Add runtime.txt with python-3.11 to force Python build on Railway (fix npm ci error)
- [x] Commit and push runtime.txt
- [x] Check new Railway logs for successful Python build, startup without port error, and custom logs (imports, DB connection)
- [x] Test /health endpoint via curl or browser
- [x] Test API endpoints (e.g., /api/reports/dimensions)
- [x] Update TODO_IMPROVEMENTS.md to mark deployment task as complete
