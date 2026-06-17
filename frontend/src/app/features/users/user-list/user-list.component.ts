import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatTableModule } from '@angular/material/table';
import { Router } from '@angular/router';

import { User } from '../../../core/models/user.model';
import { UserService } from '../../../core/services/user.service';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatPaginatorModule, MatButtonModule],
  templateUrl: './user-list.component.html',
  styleUrl: './user-list.component.scss'
})
export class UserListComponent implements OnInit {
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);

  protected readonly users = signal<User[]>([]);
  protected readonly displayedColumns = ['username', 'email', 'role', 'status', 'actions'];
  protected readonly total = signal(0);
  protected readonly pageIndex = signal(0);
  protected readonly pageSize = signal(10);

  ngOnInit(): void {
    this.load();
  }

  protected load(pageIndex = this.pageIndex(), pageSize = this.pageSize()): void {
    this.pageIndex.set(pageIndex);
    this.pageSize.set(pageSize);
    this.userService.list({ page: pageIndex + 1, page_size: pageSize }).subscribe((response) => {
      this.users.set(response.items);
      this.total.set(response.meta.total);
    });
  }

  protected handlePage(event: PageEvent): void {
    this.load(event.pageIndex, event.pageSize);
  }

  protected openCreate(): void {
    void this.router.navigate(['/users/new']);
  }

  protected editUser(user: User): void {
    void this.router.navigate(['/users', user.id, 'edit']);
  }
}
