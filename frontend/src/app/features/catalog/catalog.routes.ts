import { Routes } from '@angular/router';

import { adminGuard } from '../../core/guards/admin.guard';
import { BrandFormComponent } from './brands/brand-form.component';
import { BrandListComponent } from './brands/brand-list.component';
import { CategoryFormComponent } from './categories/category-form.component';
import { CategoryListComponent } from './categories/category-list.component';
import { SupplierFormComponent } from './suppliers/supplier-form.component';
import { SupplierListComponent } from './suppliers/supplier-list.component';

export const CATALOG_ROUTES: Routes = [
  { path: '', redirectTo: 'categories', pathMatch: 'full' },
  { path: 'categories', component: CategoryListComponent },
  { path: 'categories/new', component: CategoryFormComponent, canActivate: [adminGuard] },
  { path: 'categories/:id/edit', component: CategoryFormComponent, canActivate: [adminGuard] },
  { path: 'brands', component: BrandListComponent },
  { path: 'brands/new', component: BrandFormComponent, canActivate: [adminGuard] },
  { path: 'brands/:id/edit', component: BrandFormComponent, canActivate: [adminGuard] },
  { path: 'suppliers', component: SupplierListComponent },
  { path: 'suppliers/new', component: SupplierFormComponent, canActivate: [adminGuard] },
  { path: 'suppliers/:id/edit', component: SupplierFormComponent, canActivate: [adminGuard] }
];
