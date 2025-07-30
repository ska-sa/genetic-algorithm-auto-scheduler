import { Proposal } from "./proposal";

export interface Timetable {
    id: number;
    name: string;
    start_date: Date;
    end_date: Date;
    proposals: Proposal[];
}
