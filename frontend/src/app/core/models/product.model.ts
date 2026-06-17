export interface Product {
  id: string;
  sku: string;
  name: string;
  description: string | null;
  category_id: string | null;
  brand_id: string | null;
  supplier_id: string | null;
  cost_price: number;
  selling_price: number;
  reorder_level: number;
  is_active: boolean;
  stock_on_hand?: number;
  images: ProductImage[];
  notes: ProductNote[];
  cross_references: ProductCrossReference[];
  created_at: string;
}

export interface ProductImage {
  id: string;
  url: string;
  is_primary: boolean;
  sort_order: number;
}

export interface ProductNote {
  id: string;
  note: string;
  created_by: string;
  created_at: string;
}

export interface ProductCrossReference {
  id: string;
  product_id: string;
  equivalent_product_id: string;
  note: string | null;
}

export interface ProductCreate {
  sku: string;
  name: string;
  description?: string;
  category_id?: string;
  brand_id?: string;
  supplier_id?: string;
  cost_price: number;
  selling_price: number;
  reorder_level?: number;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  category_id?: string;
  brand_id?: string;
  supplier_id?: string;
  cost_price?: number;
  selling_price?: number;
  reorder_level?: number;
  is_active?: boolean;
}

export interface StockSnapshot {
  product_id: string;
  on_hand: number;
  as_of: string;
}
