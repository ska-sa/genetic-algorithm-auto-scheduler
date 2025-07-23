export interface ProposalModel {
    id?: string;
    description: string;
    proposal_id: string;
    owner_email: string;
    instrument_product: string;
    instrument_integration_time: string;
    instrument_band: string;
    instrument_pool_resources: string;
    lst_start: string;
    lst_start_end: string;
    simulated_duration: string;
    night_obs: string;
    avoid_sunrise_sunset: string;
    minimum_antennas: string;
    general_comments: string;
    scheduled_start_datetime: string;
}