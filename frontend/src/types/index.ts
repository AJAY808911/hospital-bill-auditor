export type BillCategory =
  | 'ROOM_RENT'
  | 'ASSOCIATE_MEDICAL'
  | 'PHARMACY'
  | 'DIAGNOSTICS'
  | 'NON_PAYABLE_CONSUMABLE'
  | 'NON_PAYABLE_ADMIN'
  | 'SURGERY_IMPLANT'
  | 'OTHER_MEDICAL'
  | 'AMBIGUOUS_UNCATEGORIZED';

export interface CategoryInfo {
  label: string;
  description: string;
  badgeColor: string;
}

export const CATEGORY_INFO: Record<BillCategory, CategoryInfo> = {
  ROOM_RENT: {
    label: 'Room Rent & ICU',
    description: 'Hospital bed, nursing room, ICU/NICU charges',
    badgeColor: 'bg-blue-100 text-blue-800 border-blue-200',
  },
  ASSOCIATE_MEDICAL: {
    label: 'Doctor & OT Charges',
    description: 'Surgeon, anesthesia, nursing & operation theatre',
    badgeColor: 'bg-indigo-100 text-indigo-800 border-indigo-200',
  },
  PHARMACY: {
    label: 'Pharmacy & Drugs',
    description: 'In-patient medications, IV fluids, injections',
    badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  },
  DIAGNOSTICS: {
    label: 'Diagnostics & Lab',
    description: 'Pathology, blood tests, radiology, scans, MRI',
    badgeColor: 'bg-cyan-100 text-cyan-800 border-cyan-200',
  },
  NON_PAYABLE_CONSUMABLE: {
    label: 'Consumables & PPE (Non-Payable)',
    description: 'Gloves, masks, PPE, syringes, cotton, wipes',
    badgeColor: 'bg-red-100 text-red-800 border-red-200',
  },
  NON_PAYABLE_ADMIN: {
    label: 'Admin Charges (Non-Payable)',
    description: 'Registration, admission fee, documentation, biowaste',
    badgeColor: 'bg-rose-100 text-rose-800 border-rose-200',
  },
  SURGERY_IMPLANT: {
    label: 'Implants & Prosthetics',
    description: 'Stents, valves, orthopedic implants, pacemakers',
    badgeColor: 'bg-purple-100 text-purple-800 border-purple-200',
  },
  OTHER_MEDICAL: {
    label: 'Other Medical Services',
    description: 'Physiotherapy, dietary advice, ambulance',
    badgeColor: 'bg-teal-100 text-teal-800 border-teal-200',
  },
  AMBIGUOUS_UNCATEGORIZED: {
    label: 'Ambiguous / Needs Review',
    description: 'Vague description requiring manual classification',
    badgeColor: 'bg-amber-100 text-amber-800 border-amber-200',
  },
};

export type RoomRentLimitType = 'FIXED_AMOUNT' | 'PERCENTAGE_OF_SI' | 'NO_LIMIT';

export interface PolicyConfig {
  id?: number;
  name: string;
  description?: string;
  sum_insured: number;
  room_rent_limit_type: RoomRentLimitType;
  room_rent_limit_amount: number;
  room_rent_limit_percentage: number;
  icu_rent_limit_amount?: number;
  apply_proportionate_deduction: boolean;
  custom_proportionate_ratio?: number | null;
  copay_percentage: number;
  deductible_amount: number;
  non_payable_categories: string[];
  length_of_stay_days: number;
  is_default?: boolean;
}

export interface BillItemInput {
  id?: string;
  original_description: string;
  category: BillCategory;
  unit_price: number;
  quantity: number;
  billed_amount: number;
  days_stay?: number;
  requires_review?: boolean;
  review_reason?: string;
}

export interface ItemAuditBreakdown {
  id?: string;
  description: string;
  category: BillCategory;
  category_label: string;
  billed_amount: number;
  allowed_amount: number;
  deduction_amount: number;
  payable_amount: number;
  deduction_reason: string;
  is_non_payable: boolean;
  is_proportionate_deduction: boolean;
  is_room_rent_excess: boolean;
  requires_review: boolean;
  review_reason?: string;
}

export interface AuditSummary {
  total_billed: number;
  total_allowed_before_policy_deductions: number;
  item_level_deductions: number;
  deductible_applied: number;
  copay_applied: number;
  copay_percentage: number;
  sum_insured_excess_applied: number;
  total_estimated_payable: number;
  total_estimated_shortfall: number;
  reconciliation_verified: boolean;
  status: 'AUDIT_CLEAN' | 'AUDIT_FLAGGED_FOR_REVIEW';
  length_of_stay_days: number;
  room_rent_billed_daily_rate: number;
  room_rent_allowed_daily_rate: number;
  proportionate_ratio_applied: number;
  assumptions_applied: string[];
  flags_and_warnings: string[];
  statutory_disclaimer: string;
}

export interface AuditResult {
  policy_name: string;
  policy_summary: Record<string, any>;
  items: ItemAuditBreakdown[];
  summary: AuditSummary;
}

export interface SavedAuditResponse {
  id: number;
  patient_name?: string;
  hospital_name?: string;
  bill_number?: string;
  policy_name: string;
  policy_id?: number;
  total_billed: number;
  total_allowed: number;
  item_level_deductions: number;
  deductible_applied: number;
  copay_applied: number;
  copay_percentage: number;
  sum_insured_excess_applied: number;
  total_estimated_payable: number;
  total_estimated_shortfall: number;
  status: string;
  length_of_stay_days: number;
  proportionate_ratio_applied: number;
  assumptions: string[];
  flags: string[];
  source_document_name?: string;
  created_at: string;
  items: {
    id: number;
    description: string;
    category: string;
    category_label?: string;
    billed_amount: number;
    allowed_amount: number;
    deduction_amount: number;
    payable_amount: number;
    deduction_reason: string;
    is_non_payable: boolean;
    is_proportionate_deduction: boolean;
    is_room_rent_excess: boolean;
    requires_review: boolean;
    review_reason?: string;
  }[];
}

export interface DashboardStatsResponse {
  total_audits_count: number;
  total_billed_volume: number;
  total_estimated_payable_volume: number;
  total_shortfall_volume: number;
  average_payable_percentage: number;
  recent_audits: {
    id: number;
    patient_name?: string;
    hospital_name?: string;
    policy_name: string;
    total_billed: number;
    total_estimated_payable: number;
    total_estimated_shortfall: number;
    status: string;
    created_at: string;
    item_count: number;
  }[];
}

export interface OCRStatusResponse {
  available: boolean;
  engine: string;
  message: string;
  install_instructions: {
    windows: string;
    linux: string;
    mac: string;
  };
}

export interface AIStatusResponse {
  enabled: boolean;
  provider: string;
  model: string;
  status: string;
  setup_guide?: string;
}

