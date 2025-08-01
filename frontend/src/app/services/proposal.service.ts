import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';
import { ProposalModel } from '../interfaces/proposal-model';

@Injectable({
  providedIn: 'root'
})
export class ProposalService {

  private url: string = `http://${environment.host}:3000/proposals`;
  private headers: HttpHeaders = new HttpHeaders({
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  });

  constructor(private httpClient: HttpClient) { }

  getProposals(): Observable<ProposalModel[]> {
    return this.httpClient.get<ProposalModel[]>(this.url, { headers: this.headers});
  }
}
