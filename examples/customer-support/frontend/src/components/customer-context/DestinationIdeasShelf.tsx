import { Upload } from "lucide-react";
import type { RefObject } from "react";

import type { BookingDestinationCard } from "../../types/support";
import { MAX_UPLOAD_SIZE_MB } from "../../lib/uploads";

type DestinationIdeasShelfProps = {
  destinations: BookingDestinationCard[];
  uploadError: string | null;
  onAttachDestination: (destination: BookingDestinationCard) => Promise<void>;
  fileInputRef: RefObject<HTMLInputElement>;
};

export function DestinationIdeasShelf({
  destinations,
  uploadError,
  onAttachDestination,
  fileInputRef,
}: DestinationIdeasShelfProps) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white/85 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
      <div className="flex flex-wrap flex-col items-start justify-between gap-4">
        <p className="text-xs uppercase tracking-[0.3em] text-blue-500 dark:text-blue-300">
          Destination ideas
        </p>
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-blue-500 hover:text-blue-600 dark:border-slate-700 dark:text-slate-200"
        >
          <Upload className="h-4 w-4" aria-hidden />
          Upload inspiration
        </button>
        <p className="w-full text-xs text-slate-500 dark:text-slate-400">
          PNG or JPG up to {MAX_UPLOAD_SIZE_MB}MB
        </p>
      </div>
      {uploadError ? (
        <p className="mt-2 text-xs font-semibold text-rose-500 dark:text-rose-300">
          {uploadError}
        </p>
      ) : null}
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {destinations.map((destination) => (
          <button
            key={destination.id}
            type="button"
            onClick={() => onAttachDestination(destination)}
            className="flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white text-left shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900"
          >
            <div
              className="h-28 bg-cover bg-center"
              style={{
                backgroundImage: `url(${
                  destination.preview_data_url ?? destination.image_url
                })`,
              }}
            />
            <div className="flex flex-1 flex-col gap-1 px-4 py-3 text-slate-800 dark:text-slate-100">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                {destination.airport}
              </p>
              <h4 className="text-base font-semibold">{destination.name}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-300">
                {destination.headline}
              </p>
              <span className="text-xs font-semibold text-blue-500 dark:text-blue-300">
                Tap to attach
              </span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
