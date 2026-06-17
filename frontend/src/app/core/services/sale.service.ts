import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/common.model';
import { Sale, SaleCreate } from '../models/sale.model';

@Injectable({ providedIn: 'root' })
export class SaleService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/sales`;

  create(data: SaleCreate): Observable<Sale> {
    return this.http.post<Sale>(this.apiUrl, data);
  }

  list(params?: Record<string, string | number | boolean>): Observable<PaginatedResponse<Sale>> {
    return this.http.get<PaginatedResponse<Sale>>(this.apiUrl, { params: params ?? {} });
  }

  getById(id: string): Observable<Sale> {
    return this.http.get<Sale>(`${this.apiUrl}/${id}`);
  }
}
