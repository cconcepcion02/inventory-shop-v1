import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { CategoryCreate, CategoryUpdate } from '../../../core/models/category.model';
import { CategoryService } from '../../../core/services/category.service';

@Component({
  selector: 'app-category-form',
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
  templateUrl: './category-form.component.html',
  styleUrl: './category-form.component.scss'
})
export class CategoryFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly categoryService = inject(CategoryService);

  protected readonly categoryId = signal<string | null>(null);
  protected readonly saving = signal(false);
  protected readonly form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    description: ['']
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.categoryId.set(id);

    if (!id) {
      return;
    }

    this.categoryService.getById(id).subscribe((category) => {
      this.form.patchValue({
        name: category.name,
        description: category.description ?? ''
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
    const id = this.categoryId();

    if (id) {
      const payload: CategoryUpdate = { name, description };
      this.categoryService.update(id, payload).subscribe({
        next: () => {
          this.saving.set(false);
          void this.router.navigate(['/catalog/categories']);
        },
        error: () => this.saving.set(false)
      });
      return;
    }

    const payload: CategoryCreate = { name, description };
    this.categoryService.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        void this.router.navigate(['/catalog/categories']);
      },
      error: () => this.saving.set(false)
    });
  }
}
