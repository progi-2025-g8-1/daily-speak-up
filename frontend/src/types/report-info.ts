export interface ReportInfo {
    video_id: string;
    year: number;
    month: number;
    day: number;
    caption: string;
    video_url: string;
    report_reasons: string[];
    user_info: {
        user_id: string;
        email: string;
        handle: string;
        profile_picture_url: string | undefined;
    };
}