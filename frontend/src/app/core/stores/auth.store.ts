import { Injectable, computed, signal } from '@angular/core';

import { User } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AuthStore {
  private _user = signal<User | null>(null);
  private _token = signal<string | null>(localStorage.getItem('access_token'));

  readonly user = this._user.asReadonly();
  readonly token = this._token.asReadonly();
  readonly isLoggedIn = computed(() => !!this._token());
  readonly isAdmin = computed(() => this._user()?.role_name === 'admin');

  setToken(token: string): void {
    this._token.set(token);
    localStorage.setItem('access_token', token);
  }

  setUser(user: User): void {
    this._user.set(user);
  }

  clear(): void {
    this._token.set(null);
    this._user.set(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}
