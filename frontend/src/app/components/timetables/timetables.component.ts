import { Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { Timetable } from '../../interfaces/timetable';
import { TimetableService } from '../../services/timetable.service';
import { CommonModule } from '@angular/common';
import { Proposal } from '../../interfaces/proposal';
import { TimetableModel } from '../../interfaces/timetable-model';
import { ProposalModel } from '../../interfaces/proposal-model';

@Component({
  selector: 'app-timetables',
  imports: [
    RouterOutlet,
    CommonModule,
  ],
  templateUrl: './timetables.component.html',
  styleUrl: './timetables.component.css'
})
export class TimetablesComponent {
  timetables: Timetable[] = [];

  isLoading: boolean = true;

  constructor(private timetableService: TimetableService, public router: Router) { }

  ngOnInit() {
    this.loadTimetables();
  }

  loadTimetables(): void {
    this.isLoading = true;
    this.timetableService.getTimetables().subscribe({
      next: (timetableData: TimetableModel[]) => {
        this.timetables = []; // C;ear timetables list
        for (const td of timetableData) {
          let proposals: Proposal[] = [];
          const proposalsData: ProposalModel[] = td.proposals;
          for (const pd of proposalsData) {
            proposals.push({
              id: Number(pd.id), // Convert the proposal ID to a number
              owner_email: pd.owner_email,
              description: pd.description,
              proposal_id: pd.proposal_id,
              instrument_product: pd.instrument_product,
              instrument_integration_time: Number(pd.instrument_integration_time),
              instrument_band: pd.instrument_band,
              instrument_pool_resources: pd.instrument_pool_resources,
              lst_start_time: pd.lst_start,
              lst_start_end_time: pd.lst_start_end,
              simulated_duration: Number(pd.simulated_duration),
              night_obs: pd.night_obs == 'yes',
              avoid_sunrise_sunset: pd.avoid_sunrise_sunset == 'yes',
              minimum_antennas: Number(pd.minimum_antennas),
              general_comments: pd.general_comments ?? "",
              score: Number(1),
              scheduled_start_datetime: pd.scheduled_start_datetime ? new Date(pd.scheduled_start_datetime) : null,
              prefered_dates_start_date: [],
              prefered_dates_end_date: [],
              avoid_dates_start_date: [],
              avoid_dates_end_date: []
            });
          }
          this.timetables.push({
            id: Number(td.id), // Convert the ID to a number
            name: td.name,
            start_date: new Date(td.start_date),
            end_date: new Date(td.end_date),
            proposals: proposals
          });
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading timetables:', error);
      }
    });
  }

  deleteTimetable(timetableId: number) : void{
    this.timetableService.deleteTimetable(timetableId).subscribe({
      next: (timetableModel: TimetableModel) => {
        //console.log(`Timetable ${timetableId} deleted successfully.`);
        this.loadTimetables();
      },
      error: (error: Error) => {
        console.error(error);
      }
    });
  }
  
  updateTimetable(timetableId: number): void {
    const timetable = this.timetables.find(t => t.id == timetableId);
    if (!timetable) {
      console.error(`Timetable with ID ${timetableId} not found.`);
      return;
    }
    const timetablesModel: TimetableModel = {
      id: timetable.id,
      name: timetable.name,
      start_date: timetable.start_date.toISOString().slice(0, 10),
      end_date: timetable.end_date.toISOString().slice(0, 10),
      proposals: timetable.proposals.map(p => ({
        id: String(p.id),
        owner_email: p.owner_email,
        description: p.description,
        proposal_id: p.proposal_id,
        instrument_product: p.instrument_product,
        instrument_integration_time: p.instrument_integration_time.toString(),
        instrument_band: p.instrument_band,
        instrument_pool_resources: p.instrument_pool_resources,
        lst_start: p.lst_start_time,
        lst_start_end: p.lst_start_end_time,
        simulated_duration: p.simulated_duration.toString(),
        night_obs: p.night_obs ? 'yes' : 'no',
        avoid_sunrise_sunset: p.avoid_sunrise_sunset ? 'yes' : 'no',
        minimum_antennas: p.minimum_antennas.toString(),
        general_comments: p.general_comments,
        scheduled_start_datetime: p.scheduled_start_datetime? p.scheduled_start_datetime.toISOString().slice(0, 19).replace('T', ' ') : ''      
      }))
    };
    this.isLoading = true;
    this.timetableService.updateTimetable(timetablesModel).subscribe({
      next: (timetableModel: TimetableModel) => {
        console.log(`Timetable ${timetableId} updated successfully.`);
        this.loadTimetables();
        this.isLoading = false;
      },
      error: (error: Error) => {
        console.error(error);
        this.isLoading = false;
      }
    });
  }

  getScheduledProposalsCount(timetable: Timetable): number {
    return timetable.proposals.filter(p => p.scheduled_start_datetime != null).length;
  }
}