import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/common.model';
import {
  Product,
  ProductCreate,
  ProductNote,
  ProductUpdate,
  StockSnapshot
} from '../models/product.model';

@Injectable({ providedIn: 'root' })
export class ProductService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/products`;

  list(params?: Record<string, string | number | boolean>): Observable<PaginatedResponse<Product>> {
    return this.http.get<PaginatedResponse<Product>>(this.apiUrl, { params: params ?? {} });
  }

  search(q: string): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.apiUrl}/search`, { params: { q } });
  }

  getById(id: string): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}/${id}`);
  }

  create(data: ProductCreate): Observable<Product> {
    return this.http.post<Product>(this.apiUrl, data);
  }

  update(id: string, data: ProductUpdate): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<unknown> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  getStock(id: string): Observable<StockSnapshot> {
    return this.http.get<StockSnapshot>(`${this.apiUrl}/${id}/stock`);
  }

  addNote(id: string, note: string): Observable<ProductNote> {
    return this.http.post<ProductNote>(`${this.apiUrl}/${id}/notes`, { note });
  }

  addCrossRef(id: string, data: { equivalent_product_id: string; note?: string }): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/${id}/cross-references`, data);
  }
}
