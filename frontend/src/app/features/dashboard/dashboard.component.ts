import { CommonModule, CurrencyPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { forkJoin } from 'rxjs';

import { ProductService } from '../../core/services/product.service';
import { ReportService } from '../../core/services/report.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, MatCardModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  private readonly productService = inject(ProductService);
  private readonly reportService = inject(ReportService);

  protected readonly stats = signal({
    products: 0,
    lowStock: 0,
    salesCount: 0,
    revenue: 0
  });

  ngOnInit(): void {
    forkJoin({
      products: this.productService.list({ page: 1, page_size: 1 }),
      lowStock: this.reportService.getLowStock(),
      sales: this.reportService.getDailySales()
    }).subscribe(({ products, lowStock, sales }) => {
      this.stats.set({
        products: products.meta.total,
        lowStock: lowStock.total,
        salesCount: sales.total_sales,
        revenue: sales.total_revenue
      });
    });
  }
}
