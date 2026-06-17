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

import { UserCreate, UserUpdate } from '../../../core/models/user.model';
import { UserService } from '../../../core/services/user.service';

@Component({
  selector: 'app-user-form',
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
  templateUrl: './user-form.component.html',
  styleUrl: './user-form.component.scss'
})
export class UserFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly userService = inject(UserService);

  protected readonly userId = signal<string | null>(null);
  protected readonly saving = signal(false);
  protected readonly roles = [
    { id: 'admin', name: 'admin' },
    { id: 'cashier', name: 'cashier' }
  ];

  protected readonly form = this.fb.nonNullable.group({
    username: ['', Validators.required],
    email: [''],
    password: [''],
    role_id: [''],
    is_active: [true]
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.userId.set(id);

    if (id) {
      this.userService.getById(id).subscribe((user) => {
        this.form.patchValue({
          username: user.username,
          email: user.email ?? '',
          role_id: user.role_id ?? user.role_name ?? '',
          is_active: user.is_active
        });
      });
    } else {
      this.form.controls.password.addValidators(Validators.required);
      this.form.controls.password.updateValueAndValidity();
    }
  }

  protected save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    this.saving.set(true);

    const id = this.userId();
    if (id) {
      const payload: UserUpdate = {
        username: raw.username,
        email: raw.email || undefined,
        password: raw.password || undefined,
        role_id: raw.role_id || undefined,
        is_active: raw.is_active
      };

      this.userService.update(id, payload).subscribe({
        next: () => {
          this.saving.set(false);
          void this.router.navigate(['/users']);
        },
        error: () => this.saving.set(false)
      });
      return;
    }

    const payload: UserCreate = {
      username: raw.username,
      email: raw.email || undefined,
      password: raw.password,
      role_id: raw.role_id || undefined
    };

    this.userService.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        void this.router.navigate(['/users']);
      },
      error: () => this.saving.set(false)
    });
  }
}
