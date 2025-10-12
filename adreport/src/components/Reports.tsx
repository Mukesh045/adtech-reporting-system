import React, { useState, useEffect } from "react";
import {
  Card,
  Select,
  DatePicker,
  Button,
  Table,
  Input,
  Space,
  Row,
  Col,
  message,
  Modal,
  Form,
  List,
  Popconfirm,
} from "antd";
import {
  SearchOutlined,
  DownloadOutlined,
  SaveOutlined,
  FolderOpenOutlined,
  DeleteOutlined,
} from "@ant-design/icons";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import moment from "moment";
import {
  ReportQueryRequest,
  ReportResponse,
  ReportData,
  SavedReport,
} from "../types";

const { Option } = Select;
const { RangePicker } = DatePicker;

const Reports: React.FC = () => {
  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  const [dimensions, setDimensions] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<string[]>([]);
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<
    [moment.Moment, moment.Moment] | null
  >(null);
  const [data, setData] = useState<ReportData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchText, setSearchText] = useState<string>("");
  const [debouncedSearchText, setDebouncedSearchText] = useState<string>("");

  const [savedReports, setSavedReports] = useState<SavedReport[]>([]);
  const [saveModalVisible, setSaveModalVisible] = useState<boolean>(false);
  const [loadModalVisible, setLoadModalVisible] = useState<boolean>(false);
  const [reportName, setReportName] = useState<string>("");

  useEffect(() => {
    fetchDimensionsAndMetrics();
  }, []);

  const fetchDimensionsAndMetrics = async (): Promise<void> => {
    try {
      const [dimRes, metRes] = await Promise.all([
        axios.get<string[]>(`${apiBaseUrl}/api/reports/dimensions`),
        axios.get<string[]>(`${apiBaseUrl}/api/reports/metrics`),
      ]);
      setDimensions(dimRes.data);
      setMetrics(metRes.data);
    } catch (error) {
      message.error("Failed to load dimensions and metrics");
    }
  };

  const handleQuery = async (): Promise<void> => {
    if (selectedDimensions.length === 0 || selectedMetrics.length === 0) {
      message.warning("Please select at least one dimension and one metric");
      return;
    }

    setLoading(true);
    try {
      const request: ReportQueryRequest = {
        dimensions: selectedDimensions,
        metrics: selectedMetrics,
        date_range: dateRange
          ? {
              start: dateRange[0].format("YYYY-MM-DD"),
              end: dateRange[1].format("YYYY-MM-DD"),
            }
          : undefined,
        group_by: selectedDimensions,
        page: 1,
        limit: 100,
      };

      const response = await axios.post<ReportResponse>(
        `${apiBaseUrl}/api/reports/query`,
        request
      );
      setData(response.data.data);
    } catch (error) {
      message.error("Failed to fetch report data");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (): Promise<void> => {
    if (selectedDimensions.length === 0 || selectedMetrics.length === 0) {
      message.warning("Please select at least one dimension and one metric");
      return;
    }

    try {
      const request: ReportQueryRequest = {
        dimensions: selectedDimensions,
        metrics: selectedMetrics,
        page: 1,
        limit: 1000,
      };
      if (dateRange) {
        request.date_range = {
          start: dateRange[0].format("YYYY-MM-DD"),
          end: dateRange[1].format("YYYY-MM-DD"),
        };
      }
      const response = await axios.post(
        `${apiBaseUrl}/api/reports/export`,
        request,
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "report.csv");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      message.error("Failed to export data");
    }
  };

  const handleDateRangeChange = (dates: any): void => {
    if (dates && dates[0] && dates[1]) {
      setDateRange([moment(dates[0].toDate()), moment(dates[1].toDate())]);
    } else {
      setDateRange(null);
    }
  };

  const handleSaveReport = async (): Promise<void> => {
    if (!reportName.trim()) {
      message.warning("Please enter a report name");
      return;
    }
    if (selectedDimensions.length === 0 || selectedMetrics.length === 0) {
      message.warning("Please select at least one dimension and one metric");
      return;
    }

    try {
      const request = {
        name: reportName,
        dimensions: selectedDimensions,
        metrics: selectedMetrics,
        date_range: dateRange
          ? {
              start: dateRange[0].format("YYYY-MM-DD"),
              end: dateRange[1].format("YYYY-MM-DD"),
            }
          : undefined,
      };
      await axios.post(
        `${apiBaseUrl}/api/reports/saved-reports`,
        request
      );
      message.success("Report saved successfully");
      setSaveModalVisible(false);
      setReportName("");
      fetchSavedReports();
    } catch (error) {
      message.error("Failed to save report");
    }
  };

  const fetchSavedReports = async (): Promise<void> => {
    try {
      const response = await axios.get<SavedReport[]>(
        `${apiBaseUrl}/api/reports/saved-reports`
      );
      setSavedReports(response.data);
    } catch (error) {
      message.error("Failed to load saved reports");
    }
  };

  const handleLoadReport = (report: SavedReport): void => {
    setSelectedDimensions(report.dimensions);
    setSelectedMetrics(report.metrics);
    if (report.date_range) {
      setDateRange([
        moment(report.date_range.start),
        moment(report.date_range.end),
      ]);
    } else {
      setDateRange(null);
    }
    setLoadModalVisible(false);
    message.success("Report loaded successfully");
  };

  const handleDeleteReport = async (reportId: string): Promise<void> => {
    try {
      await axios.delete(
        `${apiBaseUrl}/api/reports/saved-reports/${reportId}`
      );
      message.success("Report deleted successfully");
      fetchSavedReports();
    } catch (error) {
      message.error("Failed to delete report");
    }
  };

  const columns = [
    ...selectedDimensions.map((dim) => ({
      title: dim.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
      dataIndex: dim,
      key: dim,
      sorter: (a: ReportData, b: ReportData) =>
        (a[dim] || "").toString().localeCompare((b[dim] || "").toString()),
    })),
    ...selectedMetrics.map((metric) => ({
      title: metric.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
      dataIndex: metric,
      key: metric,
      sorter: (a: ReportData, b: ReportData) =>
        (Number(a[metric]) || 0) - (Number(b[metric]) || 0),
      render: (value: any) => value?.toLocaleString() || 0,
    })),
  ];

  const chartData = (data || []).slice(0, 20).map((item, index) => ({
    name: `Item ${index + 1}`,
    ...item,
  }));

  return (
    <div>
      <Card
        title={
          <span style={{ fontSize: "25px", fontWeight: "bold" }}>
            Report Builder
          </span>
        }
      >
        <Space direction="vertical" style={{ width: "100%" }}>
          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <div>
                <label htmlFor="dimensions-select" style={{ fontSize: "22px" }}>
                  Dimensions:
                </label>
                <Select
                  id="dimensions-select"
                  mode="multiple"
                  style={{ width: "100%", marginTop: 8, fontSize: "18px" }}
                  placeholder="Select dimensions"
                  value={selectedDimensions}
                  onChange={setSelectedDimensions}
                  aria-label="Select dimensions for report"
                >
                  {dimensions.map((dim) => (
                    <Option key={dim} value={dim}>
                      {dim
                        .replace(/_/g, " ")
                        .replace(/\b\w/g, (l) => l.toUpperCase())}
                    </Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={24} sm={8}>
              <div>
                <label htmlFor="metrics-select" style={{ fontSize: "22px" }}>
                  Metrics:
                </label>
                <Select
                  id="metrics-select"
                  mode="multiple"
                  style={{ width: "100%", marginTop: 8, fontSize: "18px" }}
                  placeholder="Select metrics"
                  value={selectedMetrics}
                  onChange={setSelectedMetrics}
                  aria-label="Select metrics for report"
                >
                  {metrics.map((metric) => (
                    <Option key={metric} value={metric}>
                      {metric
                        .replace(/_/g, " ")
                        .replace(/\b\w/g, (l) => l.toUpperCase())}
                    </Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={24} sm={8}>
              <div>
                <label htmlFor="date-range-picker" style={{ fontSize: "22px" }}>
                  Date Range:
                </label>
                <RangePicker
                  id="date-range-picker"
                  style={{ width: "100%", marginTop: 8 }}
                  onChange={handleDateRangeChange}
                  aria-label="Select date range for report"
                />
              </div>
            </Col>
          </Row>

          <Space direction="vertical" size="small" style={{ display: "flex" }}>
            <Button
              type="primary"
              size="large"
              block
              onClick={handleQuery}
              loading={loading}
              icon={<span style={{ fontSize: "20px" }}></span>} // Add this if you want to increase icon size
            >
              <span style={{ fontSize: "18px" }}>Generate Report</span>
            </Button>
            <Button
              icon={<DownloadOutlined style={{ fontSize: "20px" }} />}
              size="large"
              block
              onClick={handleExport}
            >
              <span style={{ fontSize: "18px" }}>Export CSV</span>
            </Button>
            <Button
              icon={<SaveOutlined style={{ fontSize: "20px" }} />}
              size="large"
              block
              onClick={() => setSaveModalVisible(true)}
            >
              <span style={{ fontSize: "18px" }}>Save Report</span>
            </Button>
            <Button
              icon={<FolderOpenOutlined style={{ fontSize: "20px" }} />}
              size="large"
              block
              onClick={() => {
                fetchSavedReports();
                setLoadModalVisible(true);
              }}
            >
              <span style={{ fontSize: "18px" }}>Load Report</span>
            </Button>
          </Space>
        </Space>
      </Card>

      {data.length > 0 && (
        <>
          <Card title="Data Visualization" style={{ marginBottom: 16 }}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                {selectedMetrics.slice(0, 3).map((metric, index) => (
                  <Line
                    key={metric}
                    type="monotone"
                    dataKey={metric}
                    stroke={`#${Math.floor(Math.random() * 16777215).toString(
                      16
                    )}`}
                    name={metric.replace(/_/g, " ")}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card title="Data Table">
            <Input
              id="search-input"
              placeholder="Search..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ marginBottom: 16, width: '100%', maxWidth: 300 }}
              aria-label="Search in report data"
            />
            <Table
              columns={columns}
              dataSource={(data || []).filter((item) =>
                Object.values(item).some((val) =>
                  String(val).toLowerCase().includes(searchText.toLowerCase())
                )
              )}
              rowKey={(record, index) => index?.toString() || "0"}
              pagination={{ pageSize: 50 }}
              scroll={{ x: 800 }}
              aria-label="Report data table"
            />
          </Card>
        </>
      )}

      <Modal
        title="Save Report"
        open={saveModalVisible}
        onOk={handleSaveReport}
        onCancel={() => setSaveModalVisible(false)}
      >
        <Form layout="vertical">
          <Form.Item label="Report Name" required>
            <Input
              value={reportName}
              onChange={(e) => setReportName(e.target.value)}
              placeholder="Enter report name"
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Load Saved Reports"
        open={loadModalVisible}
        onCancel={() => setLoadModalVisible(false)}
        footer={null}
        width={600}
      >
        <List
          dataSource={savedReports}
          renderItem={(report) => (
            <List.Item
              actions={[
                <Button type="primary" onClick={() => handleLoadReport(report)}>
                  Load
                </Button>,
                <Popconfirm
                  title="Are you sure you want to delete this report?"
                  onConfirm={() => handleDeleteReport(report.id)}
                  okText="Yes"
                  cancelText="No"
                >
                  <Button icon={<DeleteOutlined />} danger />
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                title={report.name}
                description={`Dimensions: ${report.dimensions.join(
                  ", "
                )} | Metrics: ${report.metrics.join(
                  ", "
                )} | Created: ${new Date(report.created_at).toLocaleString(
                  "en-IN",
                  { timeZone: "Asia/Kolkata" }
                )}`}
              />
            </List.Item>
          )}
        />
      </Modal>
    </div>
  );
};

export default Reports;
