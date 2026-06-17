import { CommonModule, CurrencyPipe } from '@angular/common';
import { Component, OnInit, ViewChild, computed, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginator, MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { Router } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { Brand } from '../../../core/models/brand.model';
import { Category } from '../../../core/models/category.model';
import { Product } from '../../../core/models/product.model';
import { AuthStore } from '../../../core/stores/auth.store';
import { BrandService } from '../../../core/services/brand.service';
import { CategoryService } from '../../../core/services/category.service';
import { ProductService } from '../../../core/services/product.service';

@Component({
  selector: 'app-inventory-list',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CurrencyPipe,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule
  ],
  templateUrl: './inventory-list.component.html',
  styleUrl: './inventory-list.component.scss'
})
export class InventoryListComponent implements OnInit {
  private readonly productService = inject(ProductService);
  private readonly categoryService = inject(CategoryService);
  private readonly brandService = inject(BrandService);
  private readonly router = inject(Router);
  protected readonly authStore = inject(AuthStore);

  @ViewChild(MatPaginator) paginator?: MatPaginator;

  protected readonly displayedColumns = ['sku', 'name', 'brand', 'category', 'stock', 'price', 'status', 'actions'];
  protected readonly products = signal<Product[]>([]);
  protected readonly categories = signal<Category[]>([]);
  protected readonly brands = signal<Brand[]>([]);
  protected readonly total = signal(0);
  protected readonly loading = signal(false);
  protected readonly pageSize = signal(10);
  protected readonly currentPage = signal(0);

  protected readonly categoryMap = computed(
    () => new Map(this.categories().map((c) => [c.id, c.name]))
  );
  protected readonly brandMap = computed(
    () => new Map(this.brands().map((b) => [b.id, b.name]))
  );

  protected readonly searchControl = new FormControl('', { nonNullable: true });
  protected readonly categoryControl = new FormControl<string>('');
  protected readonly brandControl = new FormControl<string>('');
  protected readonly statusControl = new FormControl<string>('');

  ngOnInit(): void {
    this.categoryService.list({ page_size: 100 }).subscribe((categories) => this.categories.set(categories));
    this.brandService.list({ page_size: 100 }).subscribe((brands) => this.brands.set(brands));

    this.searchControl.valueChanges.pipe(debounceTime(300), distinctUntilChanged()).subscribe(() => {
      this.currentPage.set(0);
      this.fetchProducts();
    });

    this.categoryControl.valueChanges.subscribe(() => {
      this.currentPage.set(0);
      this.fetchProducts();
    });

    this.brandControl.valueChanges.subscribe(() => {
      this.currentPage.set(0);
      this.fetchProducts();
    });

    this.statusControl.valueChanges.subscribe(() => {
      this.currentPage.set(0);
      this.fetchProducts();
    });

    this.fetchProducts();
  }

  protected fetchProducts(pageIndex = this.currentPage(), pageSize = this.pageSize()): void {
    this.loading.set(true);
    this.currentPage.set(pageIndex);
    this.pageSize.set(pageSize);

    const params: Record<string, string | number | boolean> = {
      page: pageIndex + 1,
      page_size: pageSize
    };

    const search = this.searchControl.value.trim();
    const categoryId = this.categoryControl.value;
    const brandId = this.brandControl.value;
    const status = this.statusControl.value;

    if (search) {
      params['q'] = search;
    }
    if (categoryId) {
      params['category_id'] = categoryId;
    }
    if (brandId) {
      params['brand_id'] = brandId;
    }
    if (status !== '' && status !== null) {
      params['is_active'] = status === 'active';
    }

    this.productService.list(params).subscribe({
      next: (response) => {
        this.products.set(response.items);
        this.total.set(response.meta.total);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  protected handlePage(event: PageEvent): void {
    this.fetchProducts(event.pageIndex, event.pageSize);
  }

  protected openCreate(): void {
    void this.router.navigate(['/inventory/new']);
  }

  protected openDetail(product: Product): void {
    void this.router.navigate(['/inventory', product.id]);
  }

  protected editProduct(product: Product, event: Event): void {
    event.stopPropagation();
    void this.router.navigate(['/inventory', product.id, 'edit']);
  }
}
