export interface StockReceiptItem {
  id?: string;
  product_id: string;
  quantity: number;
  unit_cost: number;
}

export interface StockReceipt {
  id: string;
  receipt_number: string;
  supplier_id: string | null;
  received_by: string;
  notes: string | null;
  received_at: string;
  items: StockReceiptItem[];
  created_at: string;
}

export interface StockReceiptCreate {
  supplier_id?: string;
  notes?: string;
  received_at: string;
  items: {
    product_id: string;
    quantity: number;
    unit_cost: number;
  }[];
}
