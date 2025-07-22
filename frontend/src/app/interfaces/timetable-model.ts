import { ProposalModel } from './proposal-model';

export interface TimetableModel {
    id: string;
    start_date: string;
    end_date: string;
    proposals: ProposalModel[];
}
