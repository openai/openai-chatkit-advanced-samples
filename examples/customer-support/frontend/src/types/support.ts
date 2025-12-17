export type SupportView = "overview" | "trips" | "loyalty";

export type BookingDestinationCard = {
  id: string;
  name: string;
  headline: string;
  description: string;
  airport: string;
  season: string;
  image_url: string;
  preview_data_url?: string;
  accent?: string;
  attachment_id?: string;
};

