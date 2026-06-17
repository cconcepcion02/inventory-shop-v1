import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { Router, RouterLink } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { Product } from '../../../core/models/product.model';
import { StockReceiptCreate } from '../../../core/models/stock-receipt.model';
import { Supplier } from '../../../core/models/supplier.model';
import { ProductService } from '../../../core/services/product.service';
import { ReceivingService } from '../../../core/services/receiving.service';
import { SupplierService } from '../../../core/services/supplier.service';

interface ReceiptItemFormValue {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_cost: number;
}

@Component({
  selector: 'app-receiving-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatButtonModule,
    MatIconModule,
    MatListModule
  ],
  templateUrl: './receiving-form.component.html',
  styleUrl: './receiving-form.component.scss'
})
export class ReceivingFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly supplierService = inject(SupplierService);
  private readonly productService = inject(ProductService);
  private readonly receivingService = inject(ReceivingService);
  private readonly router = inject(Router);

  protected readonly suppliers = signal<Supplier[]>([]);
  protected readonly searchResults = signal<Product[]>([]);
  protected readonly saving = signal(false);

  protected readonly form = this.fb.group({
    supplier_id: [''],
    received_at: [new Date(), Validators.required],
    notes: [''],
    product_search: [''],
    items: this.fb.array<FormGroup>([])
  });

  protected get items(): FormArray<FormGroup> {
    return this.form.get('items') as FormArray<FormGroup>;
  }

  ngOnInit(): void {
    this.supplierService.list().subscribe((suppliers) => this.suppliers.set(suppliers));
    this.form
      .get('product_search')
      ?.valueChanges.pipe(debounceTime(300), distinctUntilChanged())
      .subscribe((value) => {
        const query = (value ?? '').trim();
        if (!query) {
          this.searchResults.set([]);
          return;
        }

        this.productService.search(query).subscribe((results) => this.searchResults.set(results));
      });
  }

  protected addProduct(product: Product): void {
    this.items.push(
      this.fb.group({
        product_id: [product.id, Validators.required],
        product_name: [product.name, Validators.required],
        quantity: [1, [Validators.required, Validators.min(1)]],
        unit_cost: [product.cost_price, [Validators.required, Validators.min(0)]]
      })
    );
    this.form.patchValue({ product_search: '' });
    this.searchResults.set([]);
  }

  protected removeRow(index: number): void {
    this.items.removeAt(index);
  }

  protected submit(): void {
    if (this.form.invalid || this.items.length === 0) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    const rawItems = (raw.items ?? []) as ReceiptItemFormValue[];
    const rawDate = raw.received_at;
    const receivedAt = rawDate instanceof Date ? rawDate.toISOString() : new Date(rawDate ?? '').toISOString();
    const payload: StockReceiptCreate = {
      supplier_id: raw.supplier_id || undefined,
      notes: raw.notes || undefined,
      received_at: receivedAt,
      items: rawItems.map((item) => ({
        product_id: item.product_id,
        quantity: Number(item.quantity),
        unit_cost: Number(item.unit_cost)
      }))
    };

    this.saving.set(true);
    this.receivingService.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        void this.router.navigate(['/receiving']);
      },
      error: () => this.saving.set(false)
    });
  }
}
