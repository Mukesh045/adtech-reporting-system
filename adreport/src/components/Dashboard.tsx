import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { DollarOutlined, EyeOutlined, FileTextOutlined } from '@ant-design/icons';
import axios from 'axios';
import { DashboardData } from '../types';

interface DashboardProps {
  refreshTrigger?: number;
}

const Dashboard: React.FC<DashboardProps> = ({ refreshTrigger }) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchDashboardData();
  }, [refreshTrigger]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBaseUrl}/api/reports/summary`);
      const item = response.data;
      setData({
        total_requests: item.ad_exchange_total_requests || 0,
        total_impressions: item.ad_exchange_line_item_level_impressions || 0,
        total_clicks: item.ad_exchange_line_item_level_clicks || 0,
        total_payout: item.payout || 0,
        average_ecpm: item.average_ecpm || 0
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data', error);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
    <div className="dashboard-section"style={{ fontSize: '20px',fontWeight: 'bold' }}>
      <h2>Overall Dashboard Summary</h2>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <Card aria-label="Total Requests Statistic" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' , flexDirection: 'column'
          , padding: '20px' , boxShadow: '0 4px 8px rgba(72, 99, 191, 0.1)', borderRadius: '8px',  }}
          >
            <Statistic
               title={<span style={{ fontSize: '20px' }}>Total Requests</span>} 
              value={data?.total_requests || 0}
              prefix={<FileTextOutlined />}
              loading={loading}
              aria-label={`Total Requests: ${data?.total_requests || 0}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card aria-label="Total Impressions Statistic" style={{height: '100%',  display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' , flexDirection: 'column'
          , padding: '20px' , boxShadow: '0 4px 8px rgba(72, 99, 191, 0.1)',borderRadius: '8px'}}>
            <Statistic
              title={<span style={{ fontSize: '20px' }}>Total Impressions</span>} 
              value={data?.total_impressions || 0}
              prefix={<EyeOutlined />}
              loading={loading}
              aria-label={`Total Impressions: ${data?.total_impressions || 0}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card aria-label="Total Clicks Statistic" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' , flexDirection: 'column'
          , padding: '20px' , boxShadow: '0 4px 8px rgba(72, 99, 191, 0.1)',borderRadius: '8px' }}>
            <Statistic
              title={<span style={{ fontSize: '20px' }}>Total Clicks</span>} 
              value={data?.total_clicks || 0}
              loading={loading}
              aria-label={`Total Clicks: ${data?.total_clicks || 0}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card aria-label="Total Payout Statistic" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' , flexDirection: 'column'
          , padding: '20px' , boxShadow: '0 4px 8px rgba(72, 99, 191, 0.1)',borderRadius: '8px', }}>
            <Statistic
              title={<span style={{ fontSize: '20px' }}>Total Payout</span>} 
              value={data?.total_payout || 0}
              prefix={<DollarOutlined />}
              precision={2}
              loading={loading}
              aria-label={`Total Payout: $${data?.total_payout || 0}`}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card aria-label="Average eCPM Statistic" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' , flexDirection: 'column'
          , padding: '20px' , boxShadow: '0 4px 8px rgba(72, 99, 191, 0.1)',borderRadius: '8px', }}>
            <Statistic
              title={<span style={{ fontSize: '20px' }}>Average eCPM</span>}
              value={data?.average_ecpm || 0}
              prefix={<DollarOutlined />}
              precision={2}
              loading={loading}
              aria-label={`Average eCPM: $${data?.average_ecpm || 0}`}
            />
          </Card>
        </Col>
      </Row>
    </div>
    </div>
  );
};

export default Dashboard;
