import tokyoImageDataUrl from "../assets/tokyo.png?inline";
import santoriniImageDataUrl from "../assets/santorini.png?inline";
import parisImageDataUrl from "../assets/paris.png?inline";
import type { BookingDestinationCard } from "../types/support";

export const DEFAULT_DESTINATIONS: BookingDestinationCard[] = [
  {
    id: "tokyo",
    name: "Tokyo",
    headline: "Shibuya light trails & Daikanyama studios",
    description:
      "Jordan keeps pinning midnight art residencies around Omotesandō and ramen crawls for inspo.",
    airport: "HND",
    season: "Spring bloom · April",
    image_url: tokyoImageDataUrl,
    preview_data_url: tokyoImageDataUrl,
    accent: "#fb7185",
  },
  {
    id: "santorini",
    name: "Santorini",
    headline: "Cycladic galleries & cliffside studios",
    description:
      "Matches the loyalty offer Jordan saved for Mediterranean design tours with sea-view suites.",
    airport: "JTR",
    season: "Shoulder summer · September",
    image_url: santoriniImageDataUrl,
    preview_data_url: santoriniImageDataUrl,
    accent: "#0ea5e9",
  },
  {
    id: "paris",
    name: "Paris",
    headline: "Left Bank ateliers & Seine-side salons",
    description:
      "Their concierge dossier includes couture previews and jazz picnics leading into Bastille week.",
    airport: "CDG",
    season: "Early summer · June",
    image_url: parisImageDataUrl,
    preview_data_url: parisImageDataUrl,
    accent: "#facc15",
  },
];
