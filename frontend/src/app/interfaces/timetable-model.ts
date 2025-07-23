import { ProposalModel } from './proposal-model';

export interface TimetableModel {
    id?: number;
    start_date: string;
    end_date: string;
    proposals: ProposalModel[];
}
