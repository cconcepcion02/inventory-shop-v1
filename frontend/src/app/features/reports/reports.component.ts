import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';

import { DailySalesReport, LowStockReport } from '../../core/models/report.model';
import { ReportService } from '../../core/services/report.service';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [
    CommonModule,
    CurrencyPipe,
    DatePipe,
    MatTabsModule,
    MatCardModule,
    MatDatepickerModule,
    MatFormFieldModule,
    MatInputModule,
    MatTableModule
  ],
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss'
})
export class ReportsComponent implements OnInit {
  private readonly reportService = inject(ReportService);

  protected readonly selectedDate = signal<Date | null>(new Date());
  protected readonly dailySales = signal<DailySalesReport | null>(null);
  protected readonly lowStock = signal<LowStockReport | null>(null);
  protected readonly salesColumns = ['sale_number', 'cashier_id', 'sold_at', 'total_amount'];
  protected readonly lowStockColumns = ['sku', 'name', 'on_hand', 'reorder_level'];

  ngOnInit(): void {
    this.loadDailySales();
    this.reportService.getLowStock().subscribe((report) => this.lowStock.set(report));
  }

  protected loadDailySales(): void {
    const date = this.selectedDate();
    const formatted = date ? date.toISOString().slice(0, 10) : undefined;
    this.reportService.getDailySales(formatted).subscribe((report) => this.dailySales.set(report));
  }
}
