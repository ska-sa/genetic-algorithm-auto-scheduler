import { Component } from '@angular/core';
import { CalendarModule, DateAdapter } from 'angular-calendar';
import { adapterFactory } from 'angular-calendar/date-adapters/date-fns';

@Component({
  selector: 'app-calender',
  standalone: true,
  imports: [CalendarModule],
  templateUrl: './calender.component.html',
  styleUrls: ['./calender.component.css'], // Corrected from styleUrl to styleUrls
  providers: [
    {
      provide: DateAdapter,
      useFactory: adapterFactory,
    },
  ],
})
export class CalenderComponent {}
