import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { SupplierCreate, SupplierUpdate } from '../../../core/models/supplier.model';
import { SupplierService } from '../../../core/services/supplier.service';

@Component({
  selector: 'app-supplier-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  templateUrl: './supplier-form.component.html',
  styleUrl: './supplier-form.component.scss'
})
export class SupplierFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly supplierService = inject(SupplierService);

  protected readonly supplierId = signal<string | null>(null);
  protected readonly saving = signal(false);
  protected readonly form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    description: ['']
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.supplierId.set(id);

    if (!id) {
      return;
    }

    this.supplierService.getById(id).subscribe((supplier) => {
      this.form.patchValue({
        name: supplier.name,
        description: supplier.description ?? ''
      });
    });
  }

  protected save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    const name = raw.name.trim();
    if (!name) {
      this.form.controls.name.setErrors({ required: true });
      this.form.controls.name.markAsTouched();
      return;
    }

    this.saving.set(true);
    const description = raw.description.trim() || undefined;
    const id = this.supplierId();

    if (id) {
      const payload: SupplierUpdate = { name, description };
      this.supplierService.update(id, payload).subscribe({
        next: () => {
          this.saving.set(false);
          void this.router.navigate(['/catalog/suppliers']);
        },
        error: () => this.saving.set(false)
      });
      return;
    }

    const payload: SupplierCreate = { name, description };
    this.supplierService.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        void this.router.navigate(['/catalog/suppliers']);
      },
      error: () => this.saving.set(false)
    });
  }
}
