export interface DailySalesItem {
  sale_number: string;
  cashier_id: string;
  total_amount: number;
  sold_at: string;
}

export interface DailySalesReport {
  date: string;
  total_sales: number;
  total_revenue: number;
  items: DailySalesItem[];
}

export interface LowStockItem {
  product_id: string;
  sku: string;
  name: string;
  on_hand: number;
  reorder_level: number;
}

export interface LowStockReport {
  items: LowStockItem[];
  total: number;
}
