import { Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { ProposalModel } from '../../interfaces/proposal-model';
import { Proposal } from '../../interfaces/proposal';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TimetableService } from '../../services/timetable.service';
import { ProposalService } from '../../services/proposal.service';
import { TimetableModel } from '../../interfaces/timetable-model';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-generate-timetable',
  imports: [
    RouterOutlet,
    CommonModule,
    ReactiveFormsModule,
  ],
  templateUrl: './generate-timetable.component.html',
  styleUrl: './generate-timetable.component.css'
})
export class GenerateTimetableComponent {
  proposals: Proposal[] = [];
  proposalsSelection: boolean[] = [];

  generateTimetableForm: FormGroup;

  isLoading: boolean = true;
  showProposalsList: boolean = false;

  constructor(private formBuilder: FormBuilder, private timetableService: TimetableService, private proposalService: ProposalService, public router: Router) {
    this.generateTimetableForm = this.formBuilder.group({
      startDatetime: ['', Validators.required],
      endDatetime: ['', Validators.required]
    }, { validators: this.dateRangeValidator });
  }

  ngOnInit(): void {
    this.loadProposals();
    return;
  }

  loadProposals(): void {
    this.proposalService.getProposals().subscribe({
      next: (proposalsData: ProposalModel[]) => {
        console.log('Proposals loaded:', proposalsData);
        this.proposalsSelection = new Array(proposalsData.length).fill(false);
        for (const pd of proposalsData) {
          this.proposals.push({
            id: Number(pd.id), // Convert the proposal ID to a number
            owner_email: pd.owner_email,
            description: pd.description,
            proposal_id: pd.proposal_id,
            instrument_product: pd.instrument_product,
            instrument_integration_time: Number(pd.instrument_integration_time),
            instrument_band: pd.instrument_band,
            instrument_pool_resources: pd.instrument_pool_resources,
            lst_start_time: pd.lst_start_time,
            lst_start_end_time: pd.lst_start_end_time,
            simulated_duration: Number(pd.simulated_duration),
            night_obs: pd.night_obs.toLowerCase() === 'true',
            avoid_sunrise_sunset: pd.avoid_sunrise_sunset.toLowerCase() === 'true',
            minimum_antennas: Number(pd.minimum_antennas),
            general_comments: pd.general_comments || null,
            score: Number(1),
            scheduled_start_datetime: pd.scheduled_start_datetime ? new Date(pd.scheduled_start_datetime) : null,
            prefered_dates_start_date: [],
            prefered_dates_end_date: [],
            avoid_dates_start_date: [],
            avoid_dates_end_date: []
          });
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading proposals:', error);
      }
    });
    return;
  }

  addProposal(index: number): void {
    this.proposalsSelection[index] = true;
    this.validateProposalSelection();
    return;
  }

  removeProposal(index: number): void {
    this.proposalsSelection[index] = false;
    this.validateProposalSelection();
    return;
  }

  validateProposalSelection(): void {
    const selectedProposals = this.proposals.filter((_, index) => this.proposalsSelection[index]);
    const totalDuration = selectedProposals.reduce((total, proposal) => total + proposal.simulated_duration, 0);
    const timetableDuration =   Number(this.generateTimetableForm.get('endDatetime')?.value) - Number(this.generateTimetableForm.get('startDatetime')?.value);

    if (totalDuration > timetableDuration) {
      this.generateTimetableForm.setErrors({ 'durationExceeded': true });
    } else {
      this.generateTimetableForm.setErrors(null);
    }
    return;
  }

  cancelTimetableGeneration(): void {
    this.generateTimetableForm.reset()
    this.showProposalsList = false;
    return;
  }

  generateTimetable(): void {
    this.isLoading = true;
    const selectedProposals: ProposalModel[] = [];
    this.proposals.forEach((pd, index) => {
      if (this.proposalsSelection[index]) {
        selectedProposals.push({
          id: pd.id.toString(),
          description: pd.description,
          proposal_id: pd.proposal_id,
          owner_email: pd.owner_email,
          instrument_product: pd.instrument_product,
          instrument_integration_time: pd.instrument_integration_time.toString(),
          instrument_band: pd.instrument_band,
          instrument_pool_resources: pd.instrument_pool_resources,
          lst_start_time: pd.lst_start_time,
          lst_start_end_time: pd.lst_start_end_time,
          simulated_duration: pd.simulated_duration.toString(),
          night_obs: pd.night_obs ? 'true' : 'false',
          avoid_sunrise_sunset: pd.avoid_sunrise_sunset ? 'true' : 'false',
          minimum_antennas: pd.minimum_antennas.toString(),
          general_comments: pd.general_comments || '',
          scheduled_start_datetime: pd.scheduled_start_datetime ? pd.scheduled_start_datetime.toISOString() : ''
        });
      }
    });

    const timetableData: TimetableModel = {
      id: "0", // This will be set by the backend
      start_date: this.generateTimetableForm.get('startDatetime')?.value,
      end_date: this.generateTimetableForm.get('endDatetime')?.value,
      proposals: selectedProposals
    };

    this.timetableService.postTimetable(timetableData).subscribe({
      next: (timetable: TimetableModel) => {
        console.log('Timetable generated:', timetable);
        this.proposalsSelection = new Array(this.proposals.length).fill(false);
      },
      error: (error: any) => {
        console.error('Error generating timetable:', error);
      }
    });

    this.isLoading = false;
  }

  dateRangeValidator(group: FormGroup): { [key: string]: boolean } {
    const start = group.get('startDatetime')?.value;
    const end = group.get('endDatetime')?.value;
    return start > end ? { dateRangeInvalid: true } : {};
  }
}
