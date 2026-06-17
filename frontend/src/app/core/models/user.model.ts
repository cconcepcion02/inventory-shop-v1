export interface User {
  id: string;
  username: string;
  email: string | null;
  is_active: boolean;
  role_id: string | null;
  role_name: string | null;
  created_at: string;
}

export interface UserCreate {
  username: string;
  email?: string;
  password: string;
  role_id?: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  password?: string;
  role_id?: string;
  is_active?: boolean;
}
