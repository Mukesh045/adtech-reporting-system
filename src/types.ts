// API Response Types
export interface ImportJob {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total_records?: number;
  processed_records?: number;
  errors: string[];
  inserted?: number;
}

export interface DateRange {
  start: string;
  end: string;
}

export interface ReportQueryRequest {
  dimensions: string[];
  metrics: string[];
  filters?: Record<string, string[]>;
  date_range?: DateRange;
  page?: number;
  limit?: number;
  group_by?: string[];
}

export interface ReportData {
  [key: string]: any;
}

export interface ReportResponse {
  data: ReportData[];
  total: number;
  page: number;
  limit: number;
}

export interface DashboardData {
  total_requests: number;
  total_impressions: number;
  total_clicks: number;
  total_payout: number;
  average_ecpm: number;
}

// Component Props Types
export interface DataImportProps {}

export interface DashboardProps {}

export interface ReportsProps {}

export interface SavedReport {
  id: string;
  name: string;
  dimensions: string[];
  metrics: string[];
  date_range?: {
    start: string;
    end: string;
  };
  created_at: string;
}
