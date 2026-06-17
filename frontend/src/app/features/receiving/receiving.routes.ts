import { Routes } from '@angular/router';

import { ReceivingFormComponent } from './receiving-form/receiving-form.component';
import { ReceivingListComponent } from './receiving-list/receiving-list.component';

export const RECEIVING_ROUTES: Routes = [
  { path: '', component: ReceivingListComponent },
  { path: 'new', component: ReceivingFormComponent }
];
