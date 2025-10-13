from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from ..models import AdReport, ImportJob
from ..database import get_database
import pandas as pd
import io
import uuid
from datetime import datetime
import asyncio
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory job storage (in production, use Redis or DB)
import_jobs = {}

@router.post("/import")
async def import_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"Received file upload: {file.filename}, size: {file.size}")
    if not file.filename.endswith('.csv'):
        logger.error(f"File {file.filename} is not CSV")
        raise HTTPException(status_code=400, detail="File must be CSV")

    contents = await file.read()
    logger.info(f"Read file contents, length: {len(contents)}")

    job_id = str(uuid.uuid4())
    import_jobs[job_id] = {"job_id": job_id, "status": "pending", "progress": 0, "errors": [], "inserted": 0}
    logger.info(f"Created job {job_id}")

    # Save to DB
    import_job_doc = ImportJob(job_id=job_id, status="pending", progress=0, errors=[], inserted=0, created_at=datetime.utcnow())
    await import_job_doc.insert()

    # Process in background
    background_tasks.add_task(process_csv, job_id, contents)

    return {"job_id": job_id, "message": "Import started"}

@router.get("/import")
async def get_import_jobs():
    # Return list of recent import jobs
    jobs = await ImportJob.find().sort([("created_at", -1)]).limit(10).to_list()
    return {"jobs": [{"job_id": job.job_id, "status": job.status, "progress": job.progress, "created_at": job.created_at} for job in jobs]}

@router.get("/import/{job_id}")
async def get_import_status(job_id: str):
    # Try in-memory first
    if job_id in import_jobs:
        return import_jobs[job_id]
    # Fallback to DB
    job_doc = await ImportJob.find_one(ImportJob.job_id == job_id)
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job_doc.job_id,
        "status": job_doc.status,
        "progress": job_doc.progress,
        "errors": job_doc.errors,
        "inserted": job_doc.inserted,
        "total_records": getattr(job_doc, 'total_records', None),
        "processed_records": getattr(job_doc, 'processed_records', None)
    }

@router.get("/count")
async def get_data_count():
    db = get_database()
    collection = db.ad_reports
    count = await collection.count_documents({})
    return {"count": count}

async def process_csv(job_id: str, contents: bytes):
    logger.info(f"Starting background processing for job {job_id}")
    try:
        job = import_jobs[job_id]
        job['status'] = "processing"
        logger.info(f"Job {job_id} status set to processing")

        # Read CSV using pandas for robustness
        df = pd.read_csv(io.BytesIO(contents), header=0, encoding='utf-8-sig')
        logger.info(f"CSV read successfully, rows: {len(df)}")

        total = len(df)
        job['total_records'] = total
        
        # Clear existing data before new import
        await AdReport.delete_all()
        logger.info(f"Cleared existing data for job {job_id}")

        # Map CSV columns to internal field names
        column_mapping = {
            'Date': 'date',
            'App ID': 'mobile_app_resolved_id',
            'App Name': 'mobile_app_name',
            'Domain': 'domain',
            'Ad Unit': 'ad_unit_name',
            'Ad Unit ID': 'ad_unit_id',
            'Inventory Format': 'inventory_format_name',
            'OS Version': 'operating_system_version_name',
            'Total Requests': 'ad_exchange_total_requests',
            'Responses Served': 'ad_exchange_responses_served',
            'Match Rate': 'ad_exchange_match_rate',
            'Impressions': 'ad_exchange_line_item_level_impressions',
            'Clicks': 'ad_exchange_line_item_level_clicks',
            'CTR': 'ad_exchange_line_item_level_ctr',
            'Average eCPM': 'average_ecpm',
            'Payout': 'payout'
        }

        # Rename columns to internal names
        df.rename(columns=column_mapping, inplace=True)
        logger.info(f"Columns renamed for job {job_id}")

        # Process in batches
        batch_size = 1000
        for i in range(0, total, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            records_to_insert: List[AdReport] = []

            for index, row in batch_df.iterrows():
                try:
                    # Coerce types and handle potential missing values
                    date_val = row.get('date')
                    if pd.isna(date_val) or date_val == '':
                        date_parsed = datetime.now().date()
                    else:
                        date_parsed = pd.to_datetime(date_val, errors='coerce')
                        if pd.isna(date_parsed):
                            date_parsed = datetime.now().date()
                        else:
                            date_parsed = date_parsed.date()

                    mobile_app_resolved_id = row.get('mobile_app_resolved_id', '')
                    if pd.isna(mobile_app_resolved_id):
                        mobile_app_resolved_id = ''
                    mobile_app_resolved_id = str(mobile_app_resolved_id)

                    mobile_app_name = row.get('mobile_app_name', '')
                    if pd.isna(mobile_app_name):
                        mobile_app_name = ''
                    mobile_app_name = str(mobile_app_name)

                    domain = row.get('domain', '')
                    if pd.isna(domain):
                        domain = ''
                    domain = str(domain)

                    ad_unit_name = row.get('ad_unit_name', '')
                    if pd.isna(ad_unit_name):
                        ad_unit_name = ''
                    ad_unit_name = str(ad_unit_name)

                    ad_unit_id = row.get('ad_unit_id', '')
                    if pd.isna(ad_unit_id):
                        ad_unit_id = ''
                    ad_unit_id = str(ad_unit_id)

                    inventory_format_name = row.get('inventory_format_name', '')
                    if pd.isna(inventory_format_name):
                        inventory_format_name = ''
                    inventory_format_name = str(inventory_format_name)

                    operating_system_version_name = row.get('operating_system_version_name', '')
                    if pd.isna(operating_system_version_name):
                        operating_system_version_name = ''
                    operating_system_version_name = str(operating_system_version_name)

                    ad_exchange_total_requests = row.get('ad_exchange_total_requests', 0)
                    if pd.isna(ad_exchange_total_requests):
                        ad_exchange_total_requests = 0
                    ad_exchange_total_requests = int(ad_exchange_total_requests)

                    ad_exchange_responses_served = row.get('ad_exchange_responses_served', 0)
                    if pd.isna(ad_exchange_responses_served):
                        ad_exchange_responses_served = 0
                    ad_exchange_responses_served = int(ad_exchange_responses_served)

                    ad_exchange_match_rate = row.get('ad_exchange_match_rate', 0.0)
                    if pd.isna(ad_exchange_match_rate):
                        ad_exchange_match_rate = 0.0
                    ad_exchange_match_rate = float(ad_exchange_match_rate)

                    ad_exchange_line_item_level_impressions = row.get('ad_exchange_line_item_level_impressions', 0)
                    if pd.isna(ad_exchange_line_item_level_impressions):
                        ad_exchange_line_item_level_impressions = 0
                    ad_exchange_line_item_level_impressions = int(ad_exchange_line_item_level_impressions)

                    ad_exchange_line_item_level_clicks = row.get('ad_exchange_line_item_level_clicks', 0)
                    if pd.isna(ad_exchange_line_item_level_clicks):
                        ad_exchange_line_item_level_clicks = 0
                    ad_exchange_line_item_level_clicks = int(ad_exchange_line_item_level_clicks)

                    ad_exchange_line_item_level_ctr = row.get('ad_exchange_line_item_level_ctr', 0.0)
                    if pd.isna(ad_exchange_line_item_level_ctr):
                        ad_exchange_line_item_level_ctr = 0.0
                    ad_exchange_line_item_level_ctr = float(ad_exchange_line_item_level_ctr)

                    average_ecpm = row.get('average_ecpm', 0.0)
                    if pd.isna(average_ecpm):
                        average_ecpm = 0.0
                    average_ecpm = float(average_ecpm)

                    payout = row.get('payout', 0.0)
                    if pd.isna(payout):
                        payout = 0.0
                    payout = float(payout)

                    record_data = {
                        'report_id': job_id,
                        'date': date_parsed,
                        'mobile_app_resolved_id': mobile_app_resolved_id,
                        'mobile_app_name': mobile_app_name,
                        'domain': domain,
                        'ad_unit_name': ad_unit_name,
                        'ad_unit_id': ad_unit_id,
                        'inventory_format_name': inventory_format_name,
                        'operating_system_version_name': operating_system_version_name,
                        'ad_exchange_total_requests': ad_exchange_total_requests,
                        'ad_exchange_responses_served': ad_exchange_responses_served,
                        'ad_exchange_match_rate': ad_exchange_match_rate,
                        'ad_exchange_line_item_level_impressions': ad_exchange_line_item_level_impressions,
                        'ad_exchange_line_item_level_clicks': ad_exchange_line_item_level_clicks,
                        'ad_exchange_line_item_level_ctr': ad_exchange_line_item_level_ctr,
                        'average_ecpm': average_ecpm,
                        'payout': payout,
                    }
                    records_to_insert.append(AdReport(**record_data))
                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    error_msg = f"Row {i + index + 1}: Invalid data - {str(e)}"
                    job['errors'].append(error_msg)
                    logger.error(error_msg)

            if records_to_insert:
                try:
                    await AdReport.insert_many(records_to_insert)
                    job['inserted'] += len(records_to_insert)
                    logger.info(f"Inserted {len(records_to_insert)} records for batch {i//batch_size + 1}, job {job_id}")
                except Exception as e:
                    error_msg = f"Insert failed for batch {i//batch_size + 1}: {str(e)}"
                    job['errors'].append(error_msg)
                    logger.error(error_msg)

            job['processed_records'] = min(i + batch_size, total)
            job['progress'] = int((job['processed_records'] / total) * 100)
            logger.info(f"Progress for job {job_id}: {job['progress']}%")

        job['status'] = "completed"
        job['progress'] = 100
        logger.info(f"Job {job_id} completed successfully, inserted {job['inserted']} records")

    except Exception as e:
        error_msg = f"A critical error occurred: {str(e)}"
        job['status'] = "failed"
        job['errors'].append(error_msg)
        logger.error(f"Critical error for job {job_id}: {error_msg}")
