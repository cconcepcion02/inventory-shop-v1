import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { BrandCreate, BrandUpdate } from '../../../core/models/brand.model';
import { BrandService } from '../../../core/services/brand.service';

@Component({
  selector: 'app-brand-form',
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
  templateUrl: './brand-form.component.html',
  styleUrl: './brand-form.component.scss'
})
export class BrandFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly brandService = inject(BrandService);

  protected readonly brandId = signal<string | null>(null);
  protected readonly saving = signal(false);
  protected readonly form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    description: ['']
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.brandId.set(id);

    if (!id) {
      return;
    }

    this.brandService.getById(id).subscribe((brand) => {
      this.form.patchValue({
        name: brand.name,
        description: brand.description ?? ''
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
    const id = this.brandId();

    if (id) {
      const payload: BrandUpdate = { name, description };
      this.brandService.update(id, payload).subscribe({
        next: () => {
          this.saving.set(false);
          void this.router.navigate(['/catalog/brands']);
        },
        error: () => this.saving.set(false)
      });
      return;
    }

    const payload: BrandCreate = { name, description };
    this.brandService.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        void this.router.navigate(['/catalog/brands']);
      },
      error: () => this.saving.set(false)
    });
  }
}
