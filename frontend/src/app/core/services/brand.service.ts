import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '../../../environments/environment';
import { Brand, BrandCreate, BrandUpdate } from '../models/brand.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({ providedIn: 'root' })
export class BrandService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/brands`;

  list(params?: Record<string, string | number>): Observable<Brand[]> {
    return this.http
      .get<PaginatedResponse<Brand>>(this.apiUrl, { params: params as Record<string, string> })
      .pipe(map((r) => r.items));
  }

  listPaginated(params?: Record<string, string | number>): Observable<PaginatedResponse<Brand>> {
    return this.http.get<PaginatedResponse<Brand>>(this.apiUrl, {
      params: params as Record<string, string>
    });
  }

  getById(id: string): Observable<Brand> {
    return this.http.get<Brand>(`${this.apiUrl}/${id}`);
  }

  create(data: BrandCreate): Observable<Brand> {
    return this.http.post<Brand>(this.apiUrl, data);
  }

  update(id: string, data: BrandUpdate): Observable<Brand> {
    return this.http.put<Brand>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<unknown> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
