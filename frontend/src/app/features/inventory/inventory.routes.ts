import { Routes } from '@angular/router';

import { adminGuard } from '../../core/guards/admin.guard';
import { InventoryListComponent } from './inventory-list/inventory-list.component';
import { ProductDetailComponent } from './product-detail/product-detail.component';
import { ProductFormComponent } from './product-form/product-form.component';

export const INVENTORY_ROUTES: Routes = [
  { path: '', component: InventoryListComponent },
  { path: 'new', component: ProductFormComponent, canActivate: [adminGuard] },
  { path: ':id', component: ProductDetailComponent },
  { path: ':id/edit', component: ProductFormComponent, canActivate: [adminGuard] }
];
