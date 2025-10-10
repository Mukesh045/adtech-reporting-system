# TODO: Update Backend Endpoint for Overall Dashboard Summary

## Steps to Complete
- [ ] Read the current contents of adreport/backend/routers/reports.py to understand the existing summary endpoint
- [ ] Modify the summary endpoint to handle requests without report_id by aggregating data across all AdReport documents using MongoDB aggregation pipeline
- [ ] Add error handling for empty collections or aggregation failures
- [ ] Test the updated endpoint using curl to verify aggregated data is returned correctly
- [ ] Verify the frontend Dashboard loads the overall summary without errors

## Details
- The aggregation pipeline should use $match (if date filters needed, but for overall, no filter), $group to sum metrics like ad_exchange_total_requests, ad_exchange_line_item_level_impressions, etc., and $addFields for calculated fields like average_ecpm = (payout / impressions) * 1000
- Ensure the response format matches the frontend expectation: {ad_exchange_total_requests: sum, ad_exchange_line_item_level_impressions: sum, ad_exchange_line_item_level_clicks: sum, payout: sum, average_ecpm: calculated}
- No changes to frontend needed as it's already updated to call without report_id
