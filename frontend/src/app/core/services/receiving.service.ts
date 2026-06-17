import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/common.model';
import { StockReceipt, StockReceiptCreate } from '../models/stock-receipt.model';

@Injectable({ providedIn: 'root' })
export class ReceivingService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/receiving`;

  create(data: StockReceiptCreate): Observable<StockReceipt> {
    return this.http.post<StockReceipt>(this.apiUrl, data);
  }

  list(params?: Record<string, string | number | boolean>): Observable<PaginatedResponse<StockReceipt>> {
    return this.http.get<PaginatedResponse<StockReceipt>>(this.apiUrl, { params: params ?? {} });
  }

  getById(id: string): Observable<StockReceipt> {
    return this.http.get<StockReceipt>(`${this.apiUrl}/${id}`);
  }
}
