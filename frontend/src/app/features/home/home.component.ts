import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterLink } from '@angular/router';

interface Feature {
  icon: string;
  title: string;
  description: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [MatButtonModule, MatCardModule, MatIconModule, MatToolbarModule, RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  readonly features: Feature[] = [
    {
      icon: 'search',
      title: 'Fast Parts Search',
      description: 'Instantly search 20,000+ motorcycle parts with cross-reference support across brands.'
    },
    {
      icon: 'point_of_sale',
      title: 'Point of Sale',
      description: 'Quick and accurate POS transactions with automatic inventory deduction and receipt generation.'
    },
    {
      icon: 'inventory_2',
      title: 'Smart Inventory',
      description: 'Real-time stock tracking powered by transaction history. Never lose track of your parts.'
    },
    {
      icon: 'move_to_inbox',
      title: 'Stock Receiving',
      description: 'Streamlined receiving workflow with supplier management and automatic stock updates.'
    },
    {
      icon: 'bar_chart',
      title: 'Sales Reports',
      description: 'Daily sales summaries and low-stock alerts to keep your business running smoothly.'
    },
    {
      icon: 'build',
      title: 'Workshop Ready',
      description: 'Built for motorcycle repair shops — from standard parts to racing engine customization.'
    }
  ];

  readonly currentYear = new Date().getFullYear();
}
