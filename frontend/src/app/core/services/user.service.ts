import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/common.model';
import { User, UserCreate, UserUpdate } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/users`;

  list(params?: Record<string, string | number | boolean>): Observable<PaginatedResponse<User>> {
    return this.http.get<PaginatedResponse<User>>(this.apiUrl, { params: params ?? {} });
  }

  getById(id: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`);
  }

  create(data: UserCreate): Observable<User> {
    return this.http.post<User>(this.apiUrl, data);
  }

  update(id: string, data: UserUpdate): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<unknown> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
