import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { Product, StockSnapshot } from '../../../core/models/product.model';
import { ProductService } from '../../../core/services/product.service';
import { AuthStore } from '../../../core/stores/auth.store';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [
    CommonModule,
    CurrencyPipe,
    DatePipe,
    RouterLink,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  templateUrl: './product-detail.component.html',
  styleUrl: './product-detail.component.scss'
})
export class ProductDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);
  private readonly productService = inject(ProductService);
  protected readonly authStore = inject(AuthStore);

  protected readonly product = signal<Product | null>(null);
  protected readonly stock = signal<StockSnapshot | null>(null);
  protected readonly addingNote = signal(false);
  protected readonly noteForm = this.fb.nonNullable.group({
    note: ['', Validators.required]
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      void this.router.navigate(['/inventory']);
      return;
    }

    forkJoin({
      product: this.productService.getById(id),
      stock: this.productService.getStock(id)
    }).subscribe(({ product, stock }) => {
      this.product.set(product);
      this.stock.set(stock);
    });
  }

  protected addNote(): void {
    const product = this.product();
    if (!product || this.noteForm.invalid) {
      this.noteForm.markAllAsTouched();
      return;
    }

    this.addingNote.set(true);
    this.productService.addNote(product.id, this.noteForm.getRawValue().note).subscribe({
      next: (note) => {
        this.product.update((current) =>
          current
            ? {
                ...current,
                notes: [note, ...current.notes]
              }
            : current
        );
        this.noteForm.reset({ note: '' });
        this.addingNote.set(false);
      },
      error: () => this.addingNote.set(false)
    });
  }
}
