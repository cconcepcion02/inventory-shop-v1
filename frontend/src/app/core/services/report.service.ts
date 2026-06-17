import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { DailySalesReport, LowStockReport } from '../models/report.model';

@Injectable({ providedIn: 'root' })
export class ReportService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/reports`;

  getDailySales(date?: string): Observable<DailySalesReport> {
    const params: Record<string, string> = {};
    if (date) {
      params['date'] = date;
    }
    return this.http.get<DailySalesReport>(`${this.apiUrl}/daily-sales`, { params });
  }

  getLowStock(threshold?: number): Observable<LowStockReport> {
    const params: Record<string, number> = {};
    if (threshold !== undefined) {
      params['threshold'] = threshold;
    }
    return this.http.get<LowStockReport>(`${this.apiUrl}/low-stock`, { params });
  }
}
