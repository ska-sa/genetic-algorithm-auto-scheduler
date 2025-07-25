import { Component, OnInit } from '@angular/core';
import { CalendarComponent } from '../calendar/calendar.component';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Timetable } from '../../interfaces/timetable';
import { TimetableService } from '../../services/timetable.service';
import { TimetableModel } from '../../interfaces/timetable-model';
import { Proposal } from '../../interfaces/proposal';
import { ProposalModel } from '../../interfaces/proposal-model';
import { CommonModule } from '@angular/common';
import { eventsSignal } from '../../signal';

@Component({
  selector: 'app-timetable-details',
  imports: [
    CommonModule,
    CalendarComponent
  ],
  templateUrl: './timetable-details.component.html',
  styleUrl: './timetable-details.component.css'
})
export class TimetableDetailsComponent implements OnInit{
  id: number = 0;
  isLoading: boolean = true;
  timetable?: Timetable;

  constructor(private route: ActivatedRoute, private timetableService: TimetableService) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe({
      next: (params: ParamMap) => {
        this.id = Number(params.get('id'));
      },
      error: (error: Error) => {
        console.log(error);
      }
    });
    this.loadTimetable();
  }

  loadTimetable(): void {
    this.timetableService.getTimetable(this.id).subscribe({
      next: (timetableModel: TimetableModel) => {
        let proposals: Proposal[] = [];
        let events: any[] = [];
        timetableModel.proposals.forEach((proposalModel: ProposalModel) => {
          proposals.push({
            id: Number(proposalModel.id),
            description: proposalModel.description,
            proposal_id: proposalModel.proposal_id,
            owner_email: proposalModel.owner_email,
            instrument_product: proposalModel.instrument_product,
            instrument_integration_time: Number(proposalModel.instrument_integration_time),
            instrument_band: proposalModel.instrument_band,
            instrument_pool_resources: proposalModel.instrument_pool_resources,
            lst_start_time: proposalModel.lst_start,
            lst_start_end_time: proposalModel.lst_start_end,
            simulated_duration: Number(proposalModel.simulated_duration),
            night_obs: "yes" == proposalModel.night_obs.toLowerCase(),
            avoid_sunrise_sunset: "yes" == proposalModel.avoid_sunrise_sunset.toLowerCase(),
            minimum_antennas: Number(proposalModel.minimum_antennas),
            general_comments: proposalModel.general_comments,
            prefered_dates_start_date: [],
            prefered_dates_end_date: [],
            avoid_dates_start_date: [],
            avoid_dates_end_date: [],
            score: Number(1),
            scheduled_start_datetime: proposalModel.scheduled_start_datetime == "" ? null : new Date(proposalModel.scheduled_start_datetime)
          });

          // Skipping un scheduled proposals
          if (proposalModel.scheduled_start_datetime != "") {     
            let scheduledStartDatetime: Date = new Date(proposalModel.scheduled_start_datetime);
            let scheduledEndDatetime: Date = new Date(proposalModel.scheduled_start_datetime);
            scheduledEndDatetime.setSeconds(scheduledEndDatetime.getSeconds() + Number(proposalModel.simulated_duration));
            // appending proposals into calender events list.
            events.push({
              id: proposalModel.id,
              title: proposalModel.proposal_id,
              start: scheduledStartDatetime.toISOString(),
              end: scheduledEndDatetime.toISOString(),
              allDay: false
            });
        }
        });
        this.timetable = {
          id: Number(timetableModel.id),
          start_date: new Date(timetableModel.start_date),
          end_date: new Date(timetableModel.end_date),
          proposals: proposals
        };
        eventsSignal.set(events);
        this.isLoading = false;
      },
      error: (error: Error) => {
        console.log(error);
      }
    });
  }
}
