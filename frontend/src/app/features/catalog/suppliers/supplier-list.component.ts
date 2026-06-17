import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { Supplier } from '../../../core/models/supplier.model';
import { SupplierService } from '../../../core/services/supplier.service';
import { AuthStore } from '../../../core/stores/auth.store';

@Component({
  selector: 'app-supplier-list',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
    MatTooltipModule,
    RouterLink
  ],
  templateUrl: './supplier-list.component.html',
  styleUrl: './supplier-list.component.scss'
})
export class SupplierListComponent implements OnInit {
  private readonly supplierService = inject(SupplierService);
  protected readonly authStore = inject(AuthStore);

  protected readonly searchCtrl = new FormControl('', { nonNullable: true });
  protected readonly items = signal<Supplier[]>([]);
  protected readonly total = signal(0);
  protected readonly page = signal(0);
  protected readonly pageSize = signal(10);
  protected readonly loading = signal(false);
  protected readonly displayedColumns = computed(() =>
    this.authStore.isAdmin()
      ? ['name', 'description', 'created_at', 'actions']
      : ['name', 'description', 'created_at']
  );

  ngOnInit(): void {
    this.searchCtrl.valueChanges.pipe(debounceTime(300), distinctUntilChanged()).subscribe(() => {
      this.page.set(0);
      this.load();
    });

    this.load();
  }

  protected load(pageIndex = this.page(), size = this.pageSize()): void {
    this.loading.set(true);
    this.page.set(pageIndex);
    this.pageSize.set(size);

    const params: Record<string, string | number> = {
      page: pageIndex + 1,
      page_size: size
    };
    const search = this.searchCtrl.value.trim();
    if (search) {
      params['q'] = search;
    }

    this.supplierService.listPaginated(params).subscribe({
      next: (response) => {
        this.items.set(response.items);
        this.total.set(response.meta.total);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  protected onPage(event: PageEvent): void {
    this.load(event.pageIndex, event.pageSize);
  }

  protected deleteSupplier(supplier: Supplier): void {
    if (!this.authStore.isAdmin() || !window.confirm(`Delete ${supplier.name}?`)) {
      return;
    }

    this.loading.set(true);
    this.supplierService.delete(supplier.id).subscribe({
      next: () => {
        const nextPage = this.items().length === 1 && this.page() > 0 ? this.page() - 1 : this.page();
        this.load(nextPage, this.pageSize());
      },
      error: () => this.loading.set(false)
    });
  }
}
