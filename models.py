from beanie import Document
from datetime import date
from pymongo import IndexModel, ASCENDING

class AdReport(Document):
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
        name = "ad_reports"  # This is the collection name
        indexes = [
            # Index for fast date-range filtering
            IndexModel([("date", ASCENDING)]),
            # Compound index for common grouping/filtering scenarios
            IndexModel([("date", ASCENDING), ("mobile_app_name", ASCENDING)]),
        ]
