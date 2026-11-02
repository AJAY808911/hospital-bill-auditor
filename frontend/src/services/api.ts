import {
  AuditResult,
  DashboardStatsResponse,
  PolicyConfig,
  SavedAuditResponse,
  OCRStatusResponse,
  AIStatusResponse,
  BillItemInput,
} from '../types';

const API_BASE = '/api';

export const api = {
  // Dashboard & Statistics
  async getDashboardStats(): Promise<DashboardStatsResponse> {
    const res = await fetch(`${API_BASE}/audits/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to fetch dashboard statistics');
    return res.json();
  },

  // Policies
  async getPolicies(): Promise<PolicyConfig[]> {
    const res = await fetch(`${API_BASE}/policies`);
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },

  async createPolicy(policy: Partial<PolicyConfig>): Promise<PolicyConfig> {
    const res = await fetch(`${API_BASE}/policies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(policy),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create policy');
    }
    return res.json();
  },

  async deletePolicy(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/policies/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete policy');
  },

  // Audits & Calculations
  async previewAudit(data: {
    items: BillItemInput[];
    policy_id?: number;
    custom_policy?: PolicyConfig;
    patient_name?: string;
    hospital_name?: string;
    bill_number?: string;
  }): Promise<AuditResult> {
    const res = await fetch(`${API_BASE}/audits/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to calculate audit');
    }
    return res.json();
  },

  async saveAudit(data: {
    items: BillItemInput[];
    policy_id?: number;
    custom_policy?: PolicyConfig;
    patient_name?: string;
    hospital_name?: string;
    bill_number?: string;
    source_document_name?: string;
  }): Promise<SavedAuditResponse> {
    const res = await fetch(`${API_BASE}/audits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to save audit');
    }
    return res.json();
  },

  async getAudits(): Promise<SavedAuditResponse[]> {
    const res = await fetch(`${API_BASE}/audits`);
    if (!res.ok) throw new Error('Failed to fetch saved audits');
    return res.json();
  },

  async getAuditById(id: number): Promise<SavedAuditResponse> {
    const res = await fetch(`${API_BASE}/audits/${id}`);
    if (!res.ok) throw new Error('Failed to fetch audit details');
    return res.json();
  },

  async deleteAudit(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/audits/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete audit');
  },

  getAuditPdfUrl(id: number): string {
    return `${API_BASE}/audits/${id}/report-pdf`;
  },

  // Document Upload & Extraction
  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to extract text from document');
    }
    return res.json();
  },

  async getOCRStatus(): Promise<OCRStatusResponse> {
    const res = await fetch(`${API_BASE}/documents/ocr-status`);
    if (!res.ok) throw new Error('Failed to check OCR status');
    return res.json();
  },

  async getAIStatus(): Promise<AIStatusResponse> {
    const res = await fetch(`${API_BASE}/ai/status`);
    if (!res.ok) throw new Error('Failed to check AI status');
    return res.json();
  },

  // Section 7 Demo
  async runDemoAudit(): Promise<SavedAuditResponse> {
    const res = await fetch(`${API_BASE}/demo/run`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to execute demo audit');
    return res.json();
  },

  async getDemoData() {
    const res = await fetch(`${API_BASE}/demo/data`);
    if (!res.ok) throw new Error('Failed to fetch demo data');
    return res.json();
  },
};

