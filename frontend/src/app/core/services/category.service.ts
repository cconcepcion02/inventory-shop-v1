import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '../../../environments/environment';
import { Category, CategoryCreate, CategoryUpdate } from '../models/category.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({ providedIn: 'root' })
export class CategoryService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/categories`;

  list(params?: Record<string, string | number>): Observable<Category[]> {
    return this.http
      .get<PaginatedResponse<Category>>(this.apiUrl, { params: params as Record<string, string> })
      .pipe(map((r) => r.items));
  }

  listPaginated(params?: Record<string, string | number>): Observable<PaginatedResponse<Category>> {
    return this.http.get<PaginatedResponse<Category>>(this.apiUrl, {
      params: params as Record<string, string>
    });
  }

  getById(id: string): Observable<Category> {
    return this.http.get<Category>(`${this.apiUrl}/${id}`);
  }

  create(data: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(this.apiUrl, data);
  }

  update(id: string, data: CategoryUpdate): Observable<Category> {
    return this.http.put<Category>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<unknown> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
