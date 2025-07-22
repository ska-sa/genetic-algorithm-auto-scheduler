import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Proposal } from '../interfaces/proposal';
import { environment } from '../../environments/environment';
import { TimetableModel } from '../interfaces/timetable-model';

@Injectable({
  providedIn: 'root'
})
export class TimetableService {
  url: string = `http://${environment.host}:${3000}/timetables`;
  headers: HttpHeaders = new HttpHeaders({
      'Content-Type': 'application/json'
    });
  constructor(private httpClient: HttpClient) { }

  postTimetable(timetable: TimetableModel): Observable<TimetableModel> {
    return this.httpClient.post<TimetableModel>(this.url, timetable, { headers: this.headers });
  }

  getTimetable(timetableId: number): Observable<TimetableModel> {
    return this.httpClient.get<TimetableModel>(`${this.url}${timetableId}`, { headers: this.headers });
  }

  getTimetables(): Observable<TimetableModel[]> {
    return this.httpClient.get<TimetableModel[]>(this.url, { headers: this.headers });
  }
}
