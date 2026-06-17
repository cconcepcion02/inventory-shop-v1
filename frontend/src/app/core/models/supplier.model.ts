export interface Supplier {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
}

export interface SupplierCreate {
  name: string;
  description?: string;
}

export interface SupplierUpdate {
  name?: string;
  description?: string;
}
