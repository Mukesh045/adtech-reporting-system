from beanie import Document
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from pymongo import IndexModel, ASCENDING

class AdReport(Document):
    report_id: str
    mobile_app_resolved_id: str
    mobile_app_name: str
    domain: str
    ad_unit_name: str
    ad_unit_id: str
    inventory_format_name: str
    operating_system_version_name: str
    date: date
    ad_exchange_total_requests: int = 0
    ad_exchange_responses_served: int = 0
    ad_exchange_match_rate: float = 0.0
    ad_exchange_line_item_level_impressions: int = 0
    ad_exchange_line_item_level_clicks: int = 0
    ad_exchange_line_item_level_ctr: float = 0.0
    average_ecpm: float = 0.0
    payout: float = 0.0

    class Settings:
        name = "ad_reports"
        indexes = [
            # Index for fast date-range filtering
            IndexModel([("date", ASCENDING)]),
            # Compound index for common grouping/filtering scenarios
            IndexModel([("date", ASCENDING), ("mobile_app_name", ASCENDING)]),
            # Additional indexes for other common dimensions
            IndexModel([("domain", ASCENDING)]),
            IndexModel([("ad_unit_name", ASCENDING)]),
            IndexModel([("inventory_format_name", ASCENDING)]),
            # Index for report_id filtering
            IndexModel([("report_id", ASCENDING)]),
        ]
class ImportJob(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    total_records: Optional[int] = None
    processed_records: Optional[int] = None
    errors: List[str] = []

class SavedReport(Document):
    name: str
    dimensions: List[str]
    metrics: List[str]
    date_range: Optional[dict] = None  # {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
    created_at: datetime

    class Settings:
        name = "saved_reports"
