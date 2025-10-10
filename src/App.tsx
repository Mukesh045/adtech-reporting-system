import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import { UploadOutlined, DashboardOutlined, BarChartOutlined } from '@ant-design/icons';
import './App.css';
import DataImport from './components/DataImport';
import Dashboard from './components/Dashboard';
import Reports from './components/Reports';
import ErrorBoundary from './components/ErrorBoundary';

const { Header, Content, Sider } = Layout;

const App: React.FC = () => {
  const [selectedKey, setSelectedKey] = useState<string>('1');

  const items = [
    {
      key: '1',
      icon: <UploadOutlined />,
      label: 'Data Import',
    },
    {
      key: '2',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '3',
      icon: <BarChartOutlined />,
      label: 'Reports',
    },
  ];

  const renderContent = (): React.ReactElement => {
    switch (selectedKey) {
      case '1':
        return <DataImport />;
      case '2':
        return <Dashboard />;
      case '3':
        return <Reports />;
      default:
        return <DataImport />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <a href="#main-content" style={{ position: 'absolute', left: '-9999px' }} className="skip-link">
        Skip to main content
      </a>
      <Sider>
        <div className="logo" style={{   fontSize: 25, fontWeight: 'bold' }}>A R S</div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          onClick={(e) => setSelectedKey(e.key as string)}
          items={items}
          role="navigation"
          aria-label="Main navigation"
        />
      </Sider>
      <Layout className="site-layout">
        <Header className="site-layout-background" style={{ padding: 0 }}>
          <h2 style={{ color: 'white', marginLeft: 16,fontSize: '30px' }}>Adtech Reporting System</h2>
        </Header>
        <Content style={{ margin: '0 16px' }}>
          <div id="main-content" className="site-layout-background" style={{ padding: 24, minHeight: 360 }} role="main">
            <ErrorBoundary>
              {renderContent()}
            </ErrorBoundary>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default App;
