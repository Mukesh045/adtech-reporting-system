import requests
import time
import json
import csv
import io

# Base URL for the API (adjust if running on a different port)
BASE_URL = "http://localhost:8000"

def test_import_csv():
    """Test POST /api/data/import: Upload CSV file and return import job ID"""
    print("Testing POST /api/data/import...")

    # Create sample CSV data
    csv_data = """date,mobile_app_resolved_id,mobile_app_name,domain,ad_unit_name,ad_unit_id,inventory_format_name,operating_system_version_name,ad_exchange_total_requests,ad_exchange_responses_served,ad_exchange_match_rate,ad_exchange_line_item_level_impressions,ad_exchange_line_item_level_clicks,ad_exchange_line_item_level_ctr,average_ecpm,payout
2023-01-01,app123,Test App,example.com,Banner Ad,unit123,Banner,Android 12,1000,800,0.8,700,50,0.0714,1.5,1050.0
2023-01-02,app124,Another App,test.com,Interstitial,unit124,Interstitial,iOS 15,1500,1200,0.8,1000,75,0.075,2.0,2000.0
2023-01-03,app125,Third App,demo.com,Rewarded Video,unit125,Rewarded,iOS 14,2000,1600,0.8,1400,100,0.0714,2.5,3500.0
"""

    # Prepare the file for upload
    files = {'file': ('sample.csv', io.StringIO(csv_data), 'text/csv')}

    response = requests.post(f"{BASE_URL}/api/data/import", files=files)

    if response.status_code == 200:
        data = response.json()
        job_id = data['job_id']
        print(f"Import job started with ID: {job_id}")
        return job_id
    else:
        print(f"Failed to start import: {response.status_code} - {response.text}")
        return None

def test_import_status(job_id):
    """Test GET /api/data/import/{job_id}: Check import job status"""
    print(f"Testing GET /api/data/import/{job_id}...")

    while True:
        response = requests.get(f"{BASE_URL}/api/data/import/{job_id}")

        if response.status_code == 200:
            data = response.json()
            status = data['status']
            progress = data.get('progress', 0)
            print(f"Job status: {status}, Progress: {progress}%")

            if status == 'completed':
                print("Import completed successfully.")
                break
            elif status == 'failed':
                print(f"Import failed. Errors: {data.get('errors', [])}")
                break
            else:
                time.sleep(2)  # Wait before checking again
        else:
            print(f"Failed to get status: {response.status_code} - {response.text}")
            break

def test_get_dimensions():
    """Test GET /api/reports/dimensions: List available dimensions"""
    print("Testing GET /api/reports/dimensions...")

    response = requests.get(f"{BASE_URL}/api/reports/dimensions")

    if response.status_code == 200:
        dimensions = response.json()
        print(f"Available dimensions: {dimensions}")
        assert isinstance(dimensions, list), "Dimensions should be a list"
        assert "date" in dimensions, "Date should be in dimensions"
    else:
        print(f"Failed to get dimensions: {response.status_code} - {response.text}")

def test_get_metrics():
    """Test GET /api/reports/metrics: List available metrics"""
    print("Testing GET /api/reports/metrics...")

    response = requests.get(f"{BASE_URL}/api/reports/metrics")

    if response.status_code == 200:
        metrics = response.json()
        print(f"Available metrics: {metrics}")
        assert isinstance(metrics, list), "Metrics should be a list"
        assert "payout" in metrics, "Payout should be in metrics"
    else:
        print(f"Failed to get metrics: {response.status_code} - {response.text}")

def test_query_reports():
    """Test POST /api/reports/query: Dynamic report generation with filters, pagination, group by, aggregate"""
    print("Testing POST /api/reports/query...")

    payload = {
        "dimensions": ["mobile_app_name"],
        "metrics": ["ad_exchange_total_requests", "payout", "average_ecpm"],
        "filters": {
            "mobile_app_name": ["Test App", "Another App"]
        },
        "date_range": {
            "start": "2023-01-01",
            "end": "2023-12-31"
        },
        "page": 1,
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/api/reports/query", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"Query results: {json.dumps(data, indent=2)}")
        assert "data" in data, "Response should have 'data' key"
        assert "total" in data, "Response should have 'total' key"
        assert isinstance(data['data'], list), "Data should be a list"
    else:
        print(f"Failed to query reports: {response.status_code} - {response.text}")

def test_export_reports():
    """Test POST /api/reports/export: Export filtered data as CSV"""
    print("Testing POST /api/reports/export...")

    payload = {
        "dimensions": ["mobile_app_name"],
        "metrics": ["ad_exchange_total_requests", "payout"],
        "filters": {},
        "date_range": {
            "start": "2023-01-01",
            "end": "2023-12-31"
        },
        "page": 1,
        "limit": 50
    }

    response = requests.post(f"{BASE_URL}/api/reports/export", json=payload)

    if response.status_code == 200:
        # Save the CSV content to a file
        with open("exported_report.csv", "wb") as f:
            f.write(response.content)
        print("Exported report saved to exported_report.csv")
        # Optionally, check if it's valid CSV
        csv_content = response.content.decode('utf-8')
        lines = csv_content.split('\n')
        print(f"CSV has {len(lines)} lines (including header)")
    else:
        print(f"Failed to export reports: {response.status_code} - {response.text}")

def test_get_summary():
    """Test GET /api/reports/summary: Get dashboard summary metrics"""
    print("Testing GET /api/reports/summary...")

    response = requests.get(f"{BASE_URL}/api/reports/summary")

    if response.status_code == 200:
        data = response.json()
        print(f"Summary data: {json.dumps(data, indent=2)}")
        assert "ad_exchange_total_requests" in data, "Summary should include total requests"
        assert "average_ecpm" in data, "Summary should include average eCPM"
    else:
        print(f"Failed to get summary: {response.status_code} - {response.text}")

def test_get_latest_report_id():
    """Test GET /api/reports/latest_report_id: Get the latest report ID"""
    print("Testing GET /api/reports/latest_report_id...")

    response = requests.get(f"{BASE_URL}/api/reports/latest_report_id")

    if response.status_code == 200:
        data = response.json()
        print(f"Latest report ID: {data}")
        assert "report_id" in data, "Response should include report_id"
    else:
        print(f"Failed to get latest report ID: {response.status_code} - {response.text}")

def test_get_report_ids():
    """Test GET /api/reports/report_ids: Get all report IDs"""
    print("Testing GET /api/reports/report_ids...")

    response = requests.get(f"{BASE_URL}/api/reports/report_ids")

    if response.status_code == 200:
        data = response.json()
        print(f"Report IDs: {data}")
        assert "report_ids" in data, "Response should include report_ids"
        assert isinstance(data['report_ids'], list), "Report IDs should be a list"
    else:
        print(f"Failed to get report IDs: {response.status_code} - {response.text}")

def test_save_report():
    """Test POST /api/reports/saved-reports: Save a report configuration"""
    print("Testing POST /api/reports/saved-reports...")

    payload = {
        "name": "Test Saved Report",
        "dimensions": ["mobile_app_name", "date"],
        "metrics": ["ad_exchange_total_requests", "payout"],
        "date_range": {
            "start": "2023-01-01",
            "end": "2023-12-31"
        }
    }

    response = requests.post(f"{BASE_URL}/api/reports/saved-reports", json=payload)

    if response.status_code == 201 or response.status_code == 200:
        data = response.json()
        print(f"Saved report: {data}")
        assert "id" in data, "Response should include saved report ID"
        assert "message" in data, "Response should include success message"
        return data.get('id')
    else:
        print(f"Failed to save report: {response.status_code} - {response.text}")
        return None

def test_get_saved_reports():
    """Test GET /api/reports/saved-reports: Get all saved reports"""
    print("Testing GET /api/reports/saved-reports...")

    response = requests.get(f"{BASE_URL}/api/reports/saved-reports")

    if response.status_code == 200:
        data = response.json()
        print(f"Saved reports: {json.dumps(data, indent=2)}")
        assert isinstance(data, list), "Saved reports should be a list"
    else:
        print(f"Failed to get saved reports: {response.status_code} - {response.text}")

def test_delete_saved_report(report_id):
    """Test DELETE /api/reports/saved-reports/{report_id}: Delete a saved report"""
    if not report_id:
        print("Skipping delete test: No report ID available")
        return

    print(f"Testing DELETE /api/reports/saved-reports/{report_id}...")

    response = requests.delete(f"{BASE_URL}/api/reports/saved-reports/{report_id}")

    if response.status_code == 200:
        data = response.json()
        print(f"Deleted report: {data}")
        assert "message" in data, "Response should include success message"
    else:
        print(f"Failed to delete report: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Starting API tests...\n")

    # Test import
    job_id = test_import_csv()
    if job_id:
        test_import_status(job_id)
    print()

    # Test dimensions and metrics
    test_get_dimensions()
    print()
    test_get_metrics()
    print()

    # Test query and export (assuming data is imported)
    test_query_reports()
    print()
    test_export_reports()
    print()

    # Test summary and report IDs
    test_get_summary()
    print()
    test_get_latest_report_id()
    print()
    test_get_report_ids()
    print()

    # Test saved reports
    saved_report_id = test_save_report()
    print()
    test_get_saved_reports()
    print()

    # Test delete saved report
    test_delete_saved_report(saved_report_id)

    print("\nAPI tests completed.")
