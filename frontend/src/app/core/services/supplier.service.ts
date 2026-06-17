import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '../../../environments/environment';
import { Supplier, SupplierCreate, SupplierUpdate } from '../models/supplier.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({ providedIn: 'root' })
export class SupplierService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/suppliers`;

  list(params?: Record<string, string | number>): Observable<Supplier[]> {
    return this.http
      .get<PaginatedResponse<Supplier>>(this.apiUrl, { params: params as Record<string, string> })
      .pipe(map((r) => r.items));
  }

  listPaginated(params?: Record<string, string | number>): Observable<PaginatedResponse<Supplier>> {
    return this.http.get<PaginatedResponse<Supplier>>(this.apiUrl, {
      params: params as Record<string, string>
    });
  }

  getById(id: string): Observable<Supplier> {
    return this.http.get<Supplier>(`${this.apiUrl}/${id}`);
  }

  create(data: SupplierCreate): Observable<Supplier> {
    return this.http.post<Supplier>(this.apiUrl, data);
  }

  update(id: string, data: SupplierUpdate): Observable<Supplier> {
    return this.http.put<Supplier>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<unknown> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
