import { Routes } from '@angular/router';

import { adminGuard } from './core/guards/admin.guard';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  // Public layout — landing + login
  {
    path: '',
    loadComponent: () =>
      import('./layouts/public-layout/public-layout.component').then(
        (m) => m.PublicLayoutComponent
      ),
    children: [
      {
        path: '',
        loadChildren: () =>
          import('./features/home/home.routes').then((m) => m.HOME_ROUTES)
      },
      {
        path: 'login',
        loadChildren: () =>
          import('./features/auth/auth.routes').then((m) => m.AUTH_ROUTES)
      }
    ]
  },
  // Private layout — guarded
  {
    path: '',
    loadComponent: () =>
      import('./layouts/private-layout/private-layout.component').then(
        (m) => m.PrivateLayoutComponent
      ),
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadChildren: () =>
          import('./features/dashboard/dashboard.routes').then((m) => m.DASHBOARD_ROUTES)
      },
      {
        path: 'inventory',
        loadChildren: () =>
          import('./features/inventory/inventory.routes').then((m) => m.INVENTORY_ROUTES)
      },
      {
        path: 'pos',
        loadChildren: () =>
          import('./features/pos/pos.routes').then((m) => m.POS_ROUTES)
      },
      {
        path: 'receiving',
        canActivate: [adminGuard],
        loadChildren: () =>
          import('./features/receiving/receiving.routes').then((m) => m.RECEIVING_ROUTES)
      },
      {
        path: 'reports',
        canActivate: [adminGuard],
        loadChildren: () =>
          import('./features/reports/reports.routes').then((m) => m.REPORTS_ROUTES)
      },
      {
        path: 'users',
        canActivate: [adminGuard],
        loadChildren: () =>
          import('./features/users/users.routes').then((m) => m.USERS_ROUTES)
      }
    ]
  },
  { path: '**', redirectTo: '' }
];

