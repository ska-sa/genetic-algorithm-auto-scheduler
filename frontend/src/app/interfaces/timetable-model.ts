import { ProposalModel } from './proposal-model';

export interface TimetableModel {
    id?: number;
    name: string;
    start_date: string;
    end_date: string;
    proposals: ProposalModel[];
}
