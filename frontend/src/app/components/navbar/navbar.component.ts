import { CommonModule, NgClass } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router, RouterLink, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-navbar',
  imports: [
    RouterOutlet,
    RouterLink,
    NgClass,
    CommonModule
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit{
  id: number | null = null;
  constructor(public router: Router, private activatedRoute: ActivatedRoute) {}

  ngOnInit(): void {
    this.activatedRoute.queryParamMap.subscribe({
      next: (paramMap: ParamMap) => {
        this.id = Number(paramMap.get('id'));
      },
      error: (error: Error) => {
        console.log(error);
      }
    });
  }

  isActiveRoute(route: string): boolean {
    return this.router.url.includes(route);
  }

  navigateBack(): void {
    this.router.navigate(['/user/timetables']);
  }
}
