from fastapi import APIRouter, HTTPException, Depends
from ..models import AdReport, SavedReport
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date, datetime
import pandas as pd
from io import StringIO
from starlette.responses import StreamingResponse

router = APIRouter()

# Define allowed fields for security and validation
DIMENSIONS = [
    "mobile_app_resolved_id", "mobile_app_name", "domain", "ad_unit_name",
    "ad_unit_id", "inventory_format_name", "operating_system_version_name", "date"
]

METRICS = [
    "ad_exchange_total_requests", "ad_exchange_responses_served", "ad_exchange_match_rate",
    "ad_exchange_line_item_level_impressions", "ad_exchange_line_item_level_clicks",
    "ad_exchange_line_item_level_ctr", "average_ecpm", "payout"
]

# Pydantic models for request validation
class DateRange(BaseModel):
    start: date
    end: date

class ReportQueryRequest(BaseModel):
    dimensions: List[str]
    metrics: List[str]
    filters: Optional[Dict[str, List[str]]] = None
    date_range: Optional[DateRange] = None
    page: int = 1
    limit: int = 50

def validate_and_build_pipeline(request: ReportQueryRequest) -> List[Dict]:
    """A dependency to validate input and build the core aggregation pipeline."""
    # Validate requested dimensions and metrics against allowed lists
    if not all(d in DIMENSIONS for d in request.dimensions):
        raise HTTPException(status_code=400, detail="Invalid dimension requested.")
    if not all(m in METRICS for m in request.metrics):
        raise HTTPException(status_code=400, detail="Invalid metric requested.")

    # Validate date range
    if request.date_range and request.date_range.start > request.date_range.end:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date.")

    # 1. Match stage for filtering
    match_stage = {}
    if request.date_range:
        match_stage["date"] = {
            "$gte": datetime.combine(request.date_range.start, datetime.min.time()),
            "$lte": datetime.combine(request.date_range.end, datetime.max.time())
        }
    if request.filters:
        for key, values in request.filters.items():
            if key in DIMENSIONS and values:
                match_stage[key] = {"$in": values}

    # If no filters applied, match all documents
    if not match_stage:
        match_stage = {}

    return [{"$match": match_stage}]

@router.get("/dimensions")
async def get_dimensions():
    return DIMENSIONS

@router.get("/metrics")
async def get_metrics():
    return METRICS

@router.get("/has_data")
async def has_data():
    """Check if there's any data in the collection."""
    collection = AdReport.get_pymongo_collection()
    data_count = await collection.count_documents({})
    return {"has_data": data_count > 0}

import logging

logger = logging.getLogger("uvicorn.error")

@router.post("/query")
async def query_reports(request: ReportQueryRequest, base_pipeline: List[Dict] = Depends(validate_and_build_pipeline)):

    # Separate countable metrics from calculated rates
    sum_metrics = [m for m in request.metrics if m not in ["ad_exchange_match_rate", "ad_exchange_line_item_level_ctr", "average_ecpm"]]

    # 2. Group stage for aggregation
    group_stage = {
        "_id": {dim: f"${dim}" for dim in request.dimensions},
        # Sum only requested metrics
        **{metric: {"$sum": f"${metric}"} for metric in sum_metrics},
    }

    # Add base components for calculated fields only if requested
    if "ad_exchange_match_rate" in request.metrics:
        group_stage["ad_exchange_total_requests"] = {"$sum": "$ad_exchange_total_requests"}
        group_stage["ad_exchange_responses_served"] = {"$sum": "$ad_exchange_responses_served"}
    if "ad_exchange_line_item_level_ctr" in request.metrics or "average_ecpm" in request.metrics:
        group_stage["ad_exchange_line_item_level_impressions"] = {"$sum": "$ad_exchange_line_item_level_impressions"}
        group_stage["ad_exchange_line_item_level_clicks"] = {"$sum": "$ad_exchange_line_item_level_clicks"}
        group_stage["payout"] = {"$sum": "$payout"}

    # 3. AddFields stage to calculate the rates correctly after grouping
    add_fields_stage = {}
    if "ad_exchange_match_rate" in request.metrics:
        add_fields_stage["ad_exchange_match_rate"] = {
            "$cond": [{"$eq": ["$ad_exchange_total_requests", 0]}, 0, {"$divide": ["$ad_exchange_responses_served", "$ad_exchange_total_requests"]}]
        }
    if "ad_exchange_line_item_level_ctr" in request.metrics:
        add_fields_stage["ad_exchange_line_item_level_ctr"] = {
            "$cond": [{"$eq": ["$ad_exchange_line_item_level_impressions", 0]}, 0, {"$divide": ["$ad_exchange_line_item_level_clicks", "$ad_exchange_line_item_level_impressions"]}]
        }
    if "average_ecpm" in request.metrics:
        add_fields_stage["average_ecpm"] = {
            "$cond": [{"$eq": ["$ad_exchange_line_item_level_impressions", 0]}, 0, {"$multiply": [{"$divide": ["$payout", "$ad_exchange_line_item_level_impressions"]}, 1000]}]
        }

    # 4. Project stage to flatten the output and select final fields
    project_stage = {
        "_id": 0,
        **{dim: f"$_id.{dim}" for dim in request.dimensions},
        **{metric: f"${metric}" for metric in request.metrics}
    }

    # 5. Facet stage for pagination and total count in one query
    facet_stage = {
        "$facet": {
            "metadata": [{"$count": "total"}],
            "data": [
                {"$skip": (request.page - 1) * request.limit},
                {"$limit": request.limit}
            ]
        }
    }

    pipeline = base_pipeline + [
        {"$group": group_stage},
    ]

    if add_fields_stage:
        pipeline.append({"$addFields": add_fields_stage})

    pipeline.append({"$project": project_stage})

    # Add sort stage only if dimensions are provided
    if request.dimensions:
        pipeline.append({"$sort": {request.dimensions[0]: 1}})

    pipeline.append(facet_stage)

    logger.info(f"Aggregation pipeline: {pipeline}")

    collection = AdReport.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=None)

    logger.info(f"Aggregation results count: {len(results)}")

    if not results or not results[0]["metadata"]:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")

    return {
        "data": results[0]["data"],
        "total": results[0]["metadata"][0]["total"],
        "page": request.page,
        "limit": request.limit
    }

@router.get("/latest_report_id")
async def get_latest_report_id():
    collection = AdReport.get_pymongo_collection()
    result = await collection.find_one(sort=[("_id", -1)])
    if result:
        return {"report_id": result["report_id"]}
    return {"report_id": None}

@router.get("/report_ids")
async def get_report_ids():
    collection = AdReport.get_pymongo_collection()
    cursor = collection.distinct("report_id")
    report_ids = await cursor.to_list(length=None)
    return {"report_ids": report_ids}

@router.get("/summary")
async def get_dashboard_summary(report_id: str = None):
    """Get summary metrics for dashboard overview."""
    match_stage = {}
    if report_id:
        match_stage["report_id"] = report_id

    pipeline = [
        {"$match": match_stage} if match_stage else {},
        {
            "$group": {
                "_id": None,
                "ad_exchange_total_requests": {"$sum": "$ad_exchange_total_requests"},
                "ad_exchange_line_item_level_impressions": {"$sum": "$ad_exchange_line_item_level_impressions"},
                "ad_exchange_line_item_level_clicks": {"$sum": "$ad_exchange_line_item_level_clicks"},
                "payout": {"$sum": "$payout"},
                "total_impressions_for_ecpm": {"$sum": "$ad_exchange_line_item_level_impressions"},
                "total_payout_for_ecpm": {"$sum": "$payout"}
            }
        },
        {
            "$addFields": {
                "average_ecpm": {
                    "$cond": [
                        {"$eq": ["$total_impressions_for_ecpm", 0]},
                        0,
                        {"$multiply": [{"$divide": ["$total_payout_for_ecpm", "$total_impressions_for_ecpm"]}, 1000]}
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "ad_exchange_total_requests": 1,
                "ad_exchange_line_item_level_impressions": 1,
                "ad_exchange_line_item_level_clicks": 1,
                "payout": 1,
                "average_ecpm": 1
            }
        }
    ]

    if not match_stage:
        pipeline = pipeline[1:]  # Remove empty match

    collection = AdReport.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=None)

    logger.info(f"Summary pipeline: {pipeline}")
    logger.info(f"Summary results: {results}")

    if not results:
        return {
            "ad_exchange_total_requests": 0,
            "ad_exchange_line_item_level_impressions": 0,
            "ad_exchange_line_item_level_clicks": 0,
            "payout": 0.0,
            "average_ecpm": 0.0
        }

    return results[0]

@router.post("/export")
async def export_reports(request: ReportQueryRequest, base_pipeline: List[Dict] = Depends(validate_and_build_pipeline)):

    sum_metrics = [m for m in request.metrics if m not in ["ad_exchange_match_rate", "ad_exchange_line_item_level_ctr", "average_ecpm"]]

    group_stage = {
        "_id": {dim: f"${dim}" for dim in request.dimensions},
        **{metric: {"$sum": f"${metric}"} for metric in sum_metrics},
    }

    if "ad_exchange_match_rate" in request.metrics:
        group_stage["ad_exchange_total_requests"] = {"$sum": "$ad_exchange_total_requests"}
        group_stage["ad_exchange_responses_served"] = {"$sum": "$ad_exchange_responses_served"}
    if "ad_exchange_line_item_level_ctr" in request.metrics or "average_ecpm" in request.metrics:
        group_stage["ad_exchange_line_item_level_impressions"] = {"$sum": "$ad_exchange_line_item_level_impressions"}
        group_stage["ad_exchange_line_item_level_clicks"] = {"$sum": "$ad_exchange_line_item_level_clicks"}
        group_stage["payout"] = {"$sum": "$payout"}

    add_fields_stage = {}
    if "ad_exchange_match_rate" in request.metrics:
        add_fields_stage["ad_exchange_match_rate"] = {
            "$cond": [{"$eq": ["$ad_exchange_total_requests", 0]}, 0, {"$divide": ["$ad_exchange_responses_served", "$ad_exchange_total_requests"]}]
        }
    if "ad_exchange_line_item_level_ctr" in request.metrics:
        add_fields_stage["ad_exchange_line_item_level_ctr"] = {
            "$cond": [{"$eq": ["$ad_exchange_line_item_level_impressions", 0]}, 0, {"$divide": ["$ad_exchange_line_item_level_clicks", "$ad_exchange_line_item_level_impressions"]}]
        }
    if "average_ecpm" in request.metrics:
        add_fields_stage["average_ecpm"] = {
            "$cond": [{"$eq": ["$ad_exchange_line_item_level_impressions", 0]}, 0, {"$multiply": [{"$divide": ["$payout", "$ad_exchange_line_item_level_impressions"]}, 1000]}]
        }

    project_stage = {
        "_id": 0,
        **{dim: f"$_id.{dim}" for dim in request.dimensions},
        **{metric: f"${metric}" for metric in request.metrics}
    }

    pipeline = base_pipeline + [
        {"$group": group_stage},
    ]

    if add_fields_stage:
        pipeline.append({"$addFields": add_fields_stage})

    pipeline.append({"$project": project_stage})

    if request.dimensions:
        pipeline.append({"$sort": {request.dimensions[0]: 1}})

    collection = AdReport.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=None)

    if not results:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")
    else:
        df = pd.DataFrame(results)

    stream = StringIO()
    df.to_csv(stream, index=False)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=report.csv"
    return response

# Saved Reports endpoints
class SaveReportRequest(BaseModel):
    name: str
    dimensions: List[str]
    metrics: List[str]
    date_range: Optional[Dict[str, str]] = None

@router.post("/saved-reports")
async def save_report(request: SaveReportRequest):
    saved_report = SavedReport(
        name=request.name,
        dimensions=request.dimensions,
        metrics=request.metrics,
        date_range=request.date_range,
        created_at=datetime.now()
    )
    await saved_report.insert()
    return {"message": "Report saved successfully", "id": str(saved_report.id)}

@router.get("/saved-reports")
async def get_saved_reports():
    reports = await SavedReport.find_all().to_list()
    return [{"id": str(r.id), "name": r.name, "dimensions": r.dimensions, "metrics": r.metrics, "date_range": r.date_range, "created_at": r.created_at} for r in reports]

@router.delete("/saved-reports/{report_id}")
async def delete_saved_report(report_id: str):
    report = await SavedReport.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    await report.delete()
    return {"message": "Report deleted successfully"}
