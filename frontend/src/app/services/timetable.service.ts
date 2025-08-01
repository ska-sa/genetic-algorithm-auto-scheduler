import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { TimetableModel } from '../interfaces/timetable-model';

@Injectable({
  providedIn: 'root'
})
export class TimetableService {
  url: string = `http://${environment.host}:${environment.port}/api/v1/timetables/`;
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

  deleteTimetable(timetableId: number): Observable<TimetableModel> {
    return this.httpClient.delete<TimetableModel>(`${this.url}${timetableId}`, { headers: this.headers });
  }
}
