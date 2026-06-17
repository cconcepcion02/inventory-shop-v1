import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterLink } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { PaginatedResponse } from '../../core/models/common.model';
import { environment } from '../../../environments/environment';

export interface PublicProduct {
  id: string;
  sku: string;
  name: string;
  description: string | null;
  category_id: string | null;
  brand_id: string | null;
  is_active: boolean;
  in_stock: boolean;
  images: { id: string; url: string; is_primary: boolean; sort_order: number }[];
  created_at: string;
}

@Component({
  selector: 'app-shop',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatChipsModule,
    MatBadgeModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './shop.component.html',
  styleUrl: './shop.component.scss'
})
export class ShopComponent implements OnInit {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  products = signal<PublicProduct[]>([]);
  isLoading = signal(false);
  totalProducts = signal(0);
  pageSize = signal(12);
  currentPage = signal(0);

  searchCtrl = new FormControl('');

  ngOnInit(): void {
    this.loadProducts();

    this.searchCtrl.valueChanges.pipe(
      debounceTime(350),
      distinctUntilChanged()
    ).subscribe(() => {
      this.currentPage.set(0);
      this.loadProducts();
    });
  }

  loadProducts(): void {
    this.isLoading.set(true);
    let params = new HttpParams()
      .set('page', this.currentPage() + 1)
      .set('page_size', this.pageSize());

    const search = this.searchCtrl.value?.trim();
    if (search) params = params.set('search', search);

    this.http.get<PaginatedResponse<PublicProduct>>(
      `${this.apiUrl}/public/products`, { params }
    ).subscribe({
      next: (res) => {
        this.products.set(res.items);
        this.totalProducts.set(res.meta.total);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });
  }

  onPageChange(event: PageEvent): void {
    this.currentPage.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    this.loadProducts();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  getPrimaryImage(product: PublicProduct): string | null {
    const primary = product.images.find(i => i.is_primary) ?? product.images[0];
    return primary?.url ?? null;
  }

  readonly currentYear = new Date().getFullYear();
}
