import { CommonModule } from '@angular/common';
import { Component, computed, inject, ViewEncapsulation } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';
import { AuthStore } from '../../core/stores/auth.store';

interface NavItem {
  label: string;
  icon?: string;
  route?: string;
  adminOnly?: boolean;
  isGroup?: boolean;
}

@Component({
  selector: 'app-private-layout',
  standalone: true,
  encapsulation: ViewEncapsulation.None,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './private-layout.component.html',
  styleUrl: './private-layout.component.scss'
})
export class PrivateLayoutComponent {
  protected readonly authStore = inject(AuthStore);
  private readonly authService = inject(AuthService);

  protected readonly navItems: NavItem[] = [
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Inventory', icon: 'inventory_2', route: '/inventory' },
    { label: 'POS', icon: 'point_of_sale', route: '/pos' },
    { label: 'Receiving', icon: 'move_to_inbox', route: '/receiving', adminOnly: true },
    { label: 'Reports', icon: 'bar_chart', route: '/reports', adminOnly: true },
    { label: 'Users', icon: 'people', route: '/users', adminOnly: true },
    { label: 'Catalog', adminOnly: true, isGroup: true },
    { label: 'Categories', icon: 'category', route: '/catalog/categories', adminOnly: true },
    { label: 'Brands', icon: 'branding_watermark', route: '/catalog/brands', adminOnly: true },
    { label: 'Suppliers', icon: 'local_shipping', route: '/catalog/suppliers', adminOnly: true }
  ];

  protected readonly visibleNavItems = computed(() =>
    this.navItems.filter((item) => !item.adminOnly || this.authStore.isAdmin())
  );

  protected logout(): void {
    this.authService.logout();
  }
}
