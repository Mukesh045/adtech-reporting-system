import React, { useState } from 'react';
import { Upload, Progress, message, Card } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from 'axios';
import { ImportJob } from '../types';

const { Dragger } = Upload;

interface DataImportProps {
  onDataUploaded: () => void;
}

const DataImport: React.FC<DataImportProps> = ({ onDataUploaded }) => {
  const [importJob, setImportJob] = useState<ImportJob | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);

  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const handleUpload = async (file: File): Promise<void> => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<{ job_id: string }>(`${apiBaseUrl}/api/data/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      const jobId = response.data.job_id;
      setImportJob({ job_id: jobId, status: 'pending', progress: 0, errors: [] });
      pollJobStatus(jobId);
      message.success('Processing... File uploaded successfully.');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed';
      message.error(`Upload failed: ${errorMessage}`);
      setUploading(false);
    }
  };

  const pollJobStatus = async (jobId: string): Promise<void> => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get<ImportJob>(`${apiBaseUrl}/api/data/import/${jobId}`);
        const job = response.data;
        setImportJob(job);

        if (job.status === 'completed' || job.status === 'failed') {
          clearInterval(interval);
          setUploading(false);
          if (job.status === 'completed') {
            message.success('Import completed successfully');
            onDataUploaded(); // Notify parent component that data has been uploaded
          } else {
            message.error('Import failed');
          }
        }
      } catch (error) {
        clearInterval(interval);
        setUploading(false);
        message.error('Failed to check job status');
      }
    }, 2000);
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.csv',
    beforeUpload: (file: File) => {
      handleUpload(file);
      return false; // Prevent default upload
    },
    showUploadList: false,
  };

  return (
    <div>
      <div className="import-section">
      <Card title={<span style={{ fontSize: '25px', fontWeight: 'bold' }}>CSV Data Import</span>} aria-label="CSV Data Import Section" style={{ width: '100%' }}>
        <Dragger {...uploadProps} disabled={uploading} aria-label="CSV file upload area">
          <p className="ant-upload-drag-icon"><UploadOutlined style={{ fontSize: 80, fontWeight: 'bold' }} /></p>
          <p className="ant-upload-text" style={{ fontSize: '25px' }}><strong>Click or drag CSV file to upload</strong></p>
          <p className="ant-upload-hint" style={{ fontSize: '20px' }}><strong>Support for CSV files with adtech reporting data</strong> </p>
        </Dragger>
      </Card>
      </div>

      {importJob && (
        <Card title="Import Progress" style={{ width: '100%' }}>
          <p>Status: {importJob.status}</p>
          <Progress percent={importJob.progress} />
          {importJob.total_records && (
            <p>Processed: {importJob.processed_records} / {importJob.total_records}</p>
          )}
          {importJob.errors.length > 0 && (
            <div>
              <p>Errors:</p>
              <ul>
                {importJob.errors.map((error: string, index: number) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default DataImport;
