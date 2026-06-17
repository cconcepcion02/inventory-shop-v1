export interface Category {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
}
