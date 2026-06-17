import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Token } from '../models/auth.model';
import { User } from '../models/user.model';
import { AuthStore } from '../stores/auth.store';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly authStore = inject(AuthStore);
  private readonly router = inject(Router);
  private readonly apiUrl = environment.apiUrl;

  login(username: string, password: string): Observable<Token> {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);

    return this.http.post<Token>(`${this.apiUrl}/auth/login`, form).pipe(
      tap((token) => {
        this.authStore.setToken(token.access_token);
        localStorage.setItem('refresh_token', token.refresh_token);
      })
    );
  }

  loadMe(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/auth/me`).pipe(
      tap((user) => this.authStore.setUser(user))
    );
  }

  logout(): void {
    this.authStore.clear();
    void this.router.navigate(['/login']);
  }
}
