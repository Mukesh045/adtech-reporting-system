import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button } from 'antd';
import { UploadOutlined, DashboardOutlined, BarChartOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import './App.css';
import DataImport from './components/DataImport';
import Dashboard from './components/Dashboard';
import Reports from './components/Reports';
import ErrorBoundary from './components/ErrorBoundary';

const { Header, Content, Sider } = Layout;

const App: React.FC = () => {
  const [selectedKey, setSelectedKey] = useState<string>('1');
  const [collapsed, setCollapsed] = useState<boolean>(false);
  const [hasDataUploaded, setHasDataUploaded] = useState<boolean>(false);

  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };

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
        return <DataImport onDataUploaded={() => setHasDataUploaded(true)} />;
      case '2':
        return hasDataUploaded ? <Dashboard /> : <div>Please upload data first to view the dashboard.</div>;
      case '3':
        return hasDataUploaded ? <Reports /> : <div>Please upload data first to generate reports.</div>;
      default:
        return <DataImport onDataUploaded={() => setHasDataUploaded(true)} />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <a href="#main-content" style={{ position: 'absolute', left: '-9999px' }} className="skip-link">
        Skip to main content
      </a>
      <Sider 
        collapsible 
        collapsed={collapsed} 
        onCollapse={setCollapsed}
        breakpoint="lg"
        collapsedWidth={0}
        trigger={null}
      >
        <div className="logo" style={{ fontSize: 25, fontWeight: 'bold' }}>A R S</div>
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
        <Header className="site-layout-background" style={{ padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Button 
            type="text" 
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />} 
            onClick={toggleCollapsed} 
            style={{ 
              fontSize: '16px', 
              width: 64, 
              height: 64,
              color: 'white'
            }} 
            aria-label="Toggle sidebar"
          />
          <h2 className="app-title" style={{ color: 'white', margin: 0, flex: 1, textAlign: 'center' }}>Adtech Reporting System</h2>
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
