import { Proposal } from "./proposal";

export interface Timetable {
    id: number;
    start_date: Date;
    end_date: Date;
    proposals: Proposal[];
}
