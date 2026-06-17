import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { Brand } from '../../../core/models/brand.model';
import { Category } from '../../../core/models/category.model';
import { ProductCreate, ProductUpdate } from '../../../core/models/product.model';
import { Supplier } from '../../../core/models/supplier.model';
import { BrandService } from '../../../core/services/brand.service';
import { CategoryService } from '../../../core/services/category.service';
import { ProductService } from '../../../core/services/product.service';
import { SupplierService } from '../../../core/services/supplier.service';

@Component({
  selector: 'app-product-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatCheckboxModule
  ],
  templateUrl: './product-form.component.html',
  styleUrl: './product-form.component.scss'
})
export class ProductFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly productService = inject(ProductService);
  private readonly categoryService = inject(CategoryService);
  private readonly brandService = inject(BrandService);
  private readonly supplierService = inject(SupplierService);

  protected readonly productId = signal<string | null>(null);
  protected readonly categories = signal<Category[]>([]);
  protected readonly brands = signal<Brand[]>([]);
  protected readonly suppliers = signal<Supplier[]>([]);
  protected readonly saving = signal(false);

  protected readonly form = this.fb.nonNullable.group({
    sku: ['', Validators.required],
    name: ['', Validators.required],
    description: [''],
    category_id: [''],
    brand_id: [''],
    supplier_id: [''],
    cost_price: [0, [Validators.required, Validators.min(0)]],
    selling_price: [0, [Validators.required, Validators.min(0)]],
    reorder_level: [0, [Validators.required, Validators.min(0)]],
    is_active: [true]
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.productId.set(id);

    forkJoin({
      categories: this.categoryService.list(),
      brands: this.brandService.list(),
      suppliers: this.supplierService.list()
    }).subscribe(({ categories, brands, suppliers }) => {
      this.categories.set(categories);
      this.brands.set(brands);
      this.suppliers.set(suppliers);
    });

    if (id) {
      this.productService.getById(id).subscribe((product) => {
        this.form.patchValue({
          sku: product.sku,
          name: product.name,
          description: product.description ?? '',
          category_id: product.category_id ?? '',
          brand_id: product.brand_id ?? '',
          supplier_id: product.supplier_id ?? '',
          cost_price: product.cost_price,
          selling_price: product.selling_price,
          reorder_level: product.reorder_level,
          is_active: product.is_active
        });
      });
    }
  }

  protected save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.saving.set(true);
    const value = this.form.getRawValue();
    const id = this.productId();

    if (id) {
      const payload: ProductUpdate = {
        name: value.name,
        description: value.description || undefined,
        category_id: value.category_id || undefined,
        brand_id: value.brand_id || undefined,
        supplier_id: value.supplier_id || undefined,
        cost_price: value.cost_price,
        selling_price: value.selling_price,
        reorder_level: value.reorder_level,
        is_active: value.is_active
      };

      this.productService.update(id, payload).subscribe({
        next: (product) => {
          this.saving.set(false);
          void this.router.navigate(['/inventory', product.id]);
        },
        error: () => this.saving.set(false)
      });
      return;
    }

    const payload: ProductCreate = {
      sku: value.sku,
      name: value.name,
      description: value.description || undefined,
      category_id: value.category_id || undefined,
      brand_id: value.brand_id || undefined,
      supplier_id: value.supplier_id || undefined,
      cost_price: value.cost_price,
      selling_price: value.selling_price,
      reorder_level: value.reorder_level
    };

    this.productService.create(payload).subscribe({
      next: (product) => {
        this.saving.set(false);
        void this.router.navigate(['/inventory', product.id]);
      },
      error: () => this.saving.set(false)
    });
  }
}
