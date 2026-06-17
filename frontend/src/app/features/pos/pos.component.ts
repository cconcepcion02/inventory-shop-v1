import { CommonModule, CurrencyPipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { Product } from '../../core/models/product.model';
import { CartItem, SaleCreate } from '../../core/models/sale.model';
import { ProductService } from '../../core/services/product.service';
import { SaleService } from '../../core/services/sale.service';

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CurrencyPipe,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatListModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatSnackBarModule
  ],
  templateUrl: './pos.component.html',
  styleUrl: './pos.component.scss'
})
export class PosComponent implements OnInit {
  private readonly productService = inject(ProductService);
  private readonly saleService = inject(SaleService);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly searchControl = new FormControl('', { nonNullable: true });
  protected readonly cart = signal<CartItem[]>([]);
  protected readonly searchResults = signal<Product[]>([]);
  protected readonly amountTendered = signal(0);
  protected readonly isSubmitting = signal(false);
  protected readonly displayedColumns = ['name', 'quantity', 'price', 'subtotal', 'actions'];

  protected readonly totalAmount = computed(() =>
    this.cart().reduce((sum, item) => sum + item.quantity * item.unit_price, 0)
  );
  protected readonly change = computed(() => this.amountTendered() - this.totalAmount());

  ngOnInit(): void {
    this.searchControl.valueChanges.pipe(debounceTime(300), distinctUntilChanged()).subscribe((value) => {
      const query = value.trim();
      if (!query) {
        this.searchResults.set([]);
        return;
      }

      this.productService.search(query).subscribe((results) => this.searchResults.set(results));
    });
  }

  protected addToCart(product: Product): void {
    this.cart.update((items) => {
      const existing = items.find((item) => item.product.id === product.id);
      if (existing) {
        return items.map((item) =>
          item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }

      return [...items, { product, quantity: 1, unit_price: product.selling_price }];
    });
  }

  protected updateQuantity(productId: string, delta: number): void {
    this.cart.update((items) =>
      items
        .map((item) =>
          item.product.id === productId ? { ...item, quantity: Math.max(0, item.quantity + delta) } : item
        )
        .filter((item) => item.quantity > 0)
    );
  }

  protected removeItem(productId: string): void {
    this.cart.update((items) => items.filter((item) => item.product.id !== productId));
  }

  protected updateTendered(value: string): void {
    this.amountTendered.set(Number(value) || 0);
  }

  protected completeSale(): void {
    if (!this.cart().length || this.change() < 0) {
      return;
    }

    const payload: SaleCreate = {
      items: this.cart().map((item) => ({
        product_id: item.product.id,
        quantity: item.quantity,
        unit_price: item.unit_price,
        subtotal: item.quantity * item.unit_price
      })),
      amount_tendered: this.amountTendered()
    };

    this.isSubmitting.set(true);
    this.saleService.create(payload).subscribe({
      next: (sale) => {
        this.cart.set([]);
        this.searchResults.set([]);
        this.searchControl.setValue('');
        this.amountTendered.set(0);
        this.isSubmitting.set(false);
        this.snackBar.open(`Sale ${sale.sale_number} completed successfully.`, 'Close', { duration: 3000 });
      },
      error: () => {
        this.isSubmitting.set(false);
        this.snackBar.open('Failed to complete sale.', 'Close', { duration: 3000 });
      }
    });
  }
}
