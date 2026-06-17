import { Product } from './product.model';

export interface SaleItem {
  id?: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Sale {
  id: string;
  sale_number: string;
  cashier_id: string;
  total_amount: number;
  amount_tendered: number;
  change_amount: number;
  notes: string | null;
  sold_at: string;
  items: SaleItem[];
  created_at: string;
}

export interface SaleCreate {
  items: {
    product_id: string;
    quantity: number;
    unit_price: number;
    subtotal: number;
  }[];
  amount_tendered: number;
  notes?: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
  unit_price: number;
}
