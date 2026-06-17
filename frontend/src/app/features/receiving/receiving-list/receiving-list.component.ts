import { CommonModule, DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatTableModule } from '@angular/material/table';
import { Router } from '@angular/router';

import { StockReceipt } from '../../../core/models/stock-receipt.model';
import { ReceivingService } from '../../../core/services/receiving.service';

@Component({
  selector: 'app-receiving-list',
  standalone: true,
  imports: [CommonModule, DatePipe, MatTableModule, MatPaginatorModule, MatButtonModule],
  templateUrl: './receiving-list.component.html',
  styleUrl: './receiving-list.component.scss'
})
export class ReceivingListComponent implements OnInit {
  private readonly receivingService = inject(ReceivingService);
  private readonly router = inject(Router);

  protected readonly receipts = signal<StockReceipt[]>([]);
  protected readonly displayedColumns = ['receipt_number', 'supplier', 'received_at', 'items'];
  protected readonly total = signal(0);
  protected readonly pageSize = signal(10);
  protected readonly pageIndex = signal(0);

  ngOnInit(): void {
    this.load();
  }

  protected load(pageIndex = this.pageIndex(), pageSize = this.pageSize()): void {
    this.pageIndex.set(pageIndex);
    this.pageSize.set(pageSize);
    this.receivingService.list({ page: pageIndex + 1, page_size: pageSize }).subscribe((response) => {
      this.receipts.set(response.items);
      this.total.set(response.meta.total);
    });
  }

  protected handlePage(event: PageEvent): void {
    this.load(event.pageIndex, event.pageSize);
  }

  protected openCreate(): void {
    void this.router.navigate(['/receiving/new']);
  }
}
