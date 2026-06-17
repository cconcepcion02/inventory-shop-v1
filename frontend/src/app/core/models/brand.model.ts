export interface Brand {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
}

export interface BrandCreate {
  name: string;
  description?: string;
}

export interface BrandUpdate {
  name?: string;
  description?: string;
}
