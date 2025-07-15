import { Time } from "@angular/common";

export interface Proposal {
    id: number;
    description: string;
    proposal_id: string;
    owner_email: string;
    instrument_product: string;
    instrument_integration_time: number;
    instrument_band: string;
    instrument_pool_resources: string;
    lst_start_time: Time;
    lst_start_end_time: Time;
    simulated_duration: number;
    night_obs: boolean;
    avoid_sunrise_sunset: boolean;
    minimum_antennas: number;
    general_comments: string;
    prefered_dates_start_date: Date[];
    prefered_dates_end_date: Date[];
    avoid_dates_start_date: Date[];
    avoid_dates_end_date: Date[];
    score: number;
    scheduled_start_datetime: Date | null;
}
