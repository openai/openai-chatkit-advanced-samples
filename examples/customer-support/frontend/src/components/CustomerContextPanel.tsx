import type { Attachment } from "@openai/chatkit";
import { Mail, Phone } from "lucide-react";
import clsx from "clsx";
import { useRef, useState } from "react";
import type { ReactNode } from "react";

import type { CustomerProfile } from "../hooks/useCustomerContext";
import type { BookingDestinationCard, SupportView } from "../types/support";
import type { ChatKitInstance } from "./ChatKitPanel";
import { DEFAULT_DESTINATIONS } from "../lib/destinations";
import { MAX_UPLOAD_BYTES, MAX_UPLOAD_SIZE_MB } from "../lib/uploads";
import { SUPPORT_CHATKIT_API_URL } from "../lib/config";
import { DestinationIdeasShelf } from "./customer-context/DestinationIdeasShelf";
import { LoyaltyView } from "./customer-context/LoyaltyView";
import { TripsView } from "./customer-context/TripsView";

type CustomerContextPanelProps = {
  profile: CustomerProfile | null;
  loading: boolean;
  error: string | null;
  view: SupportView;
  onViewChange: (view: SupportView) => void;
  chatkit: ChatKitInstance | null;
};

const NAV_ITEMS: { id: SupportView; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "trips", label: "Trips" },
  { id: "loyalty", label: "Loyalty" },
];

export function CustomerContextPanel({
  profile,
  loading,
  error,
  view,
  onViewChange,
  chatkit,
}: CustomerContextPanelProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  if (loading && !profile) {
    return (
      <section className="flex h-full flex-col gap-4 rounded-3xl border border-slate-200/60 bg-white/80 p-6 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/70 dark:shadow-[0_45px_95px_-55px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
        <header>
          <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
            Customer profile
          </h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">
            Loading customer data…
          </p>
        </header>
        <div className="flex flex-1 items-center justify-center">
          <span className="text-sm text-slate-500 dark:text-slate-400">
            Fetching the latest itinerary and services…
          </span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="flex h-full flex-col gap-4 rounded-3xl border border-rose-200 bg-rose-50/60 p-6 text-rose-700 shadow-sm dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-200">
        <header>
          <h2 className="text-xl font-semibold">Customer profile</h2>
        </header>
        <p className="text-sm">{error}</p>
      </section>
    );
  }

  if (!profile) {
    return (
      <section className="flex h-full flex-col gap-4 rounded-3xl border border-slate-200/60 bg-white/80 p-6 text-slate-600 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/70 dark:text-slate-300 dark:shadow-[0_45px_95px_-55px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
        <header>
          <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
            Customer profile
          </h2>
        </header>
        <div className="flex flex-1 items-center justify-center">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Start a chat to load the traveller&apos;s account context.
          </p>
        </div>
      </section>
    );
  }

  const inspirationDestinations = DEFAULT_DESTINATIONS;

  const attachDestinationImage = async (
    destination: BookingDestinationCard
  ) => {
    if (!chatkit) {
      setUploadError("Open the chat to attach inspiration.");
      return;
    }
    setUploadError(null);
    try {
      const file = await dataUrlToFile(
        destination.preview_data_url ?? destination.image_url,
        `${destination.name}.jpg`
      );
      if (file.size > MAX_UPLOAD_BYTES) {
        setUploadError(
          `Use an image under ${MAX_UPLOAD_SIZE_MB}MB so it streams quickly.`
        );
        return;
      }
      const attachment = await uploadImageAttachment(chatkit, file);
      await chatkit.setComposerValue({
        text: `Let's explore flights to ${destination.name}.`,
        attachments: [attachment],
      });
      await chatkit.focusComposer();
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Unable to attach that destination.";
      setUploadError(message);
    }
  };

  const handleCustomUpload = async (file: File) => {
    if (file.size > MAX_UPLOAD_BYTES) {
      setUploadError(
        `Use an image under ${MAX_UPLOAD_SIZE_MB}MB so it streams quickly.`
      );
      return;
    }
    if (!chatkit) {
      setUploadError("Open the chat to attach inspiration.");
      return;
    }
    setUploadError(null);
    try {
      const attachment = await uploadImageAttachment(chatkit, file);
      await chatkit.setComposerValue({
        text: "Book a flight to this destination.",
        attachments: [attachment],
      });
      await chatkit.focusComposer();
    } catch (uploadErr) {
      const message =
        uploadErr instanceof Error
          ? uploadErr.message
          : "Unable to attach that photo.";
      setUploadError(message);
    }
  };

  const headerContent = (
    <header className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-blue-500 dark:text-blue-300">
            Concierge customer
          </p>
          <h2 className="text-2xl font-semibold text-slate-800 dark:text-slate-100">
            {profile.name}
          </h2>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-slate-600 dark:text-slate-300">
            <span className="inline-flex items-center gap-1.5">
              <Mail className="h-4 w-4" aria-hidden />
              {profile.email}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Phone className="h-4 w-4" aria-hidden />
              {profile.phone}
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 dark:border-blue-900/60 dark:bg-blue-950/30 dark:text-blue-200">
          {profile.loyalty_status} · {profile.loyalty_id}
        </div>
      </div>
      <nav className="flex flex-wrap gap-2 text-sm">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onViewChange(item.id)}
            className={clsx(
              "rounded-full px-4 py-2 font-medium transition",
              view === item.id
                ? "bg-slate-900 text-white shadow-lg dark:bg-slate-100 dark:text-slate-900"
                : "bg-slate-100 text-slate-500 hover:text-slate-800 dark:bg-slate-900/70 dark:text-slate-400"
            )}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </header>
  );

  let bodyContent: ReactNode = null;
  if (view === "trips") {
    bodyContent = <TripsView profile={profile} />;
  } else if (view === "loyalty") {
    bodyContent = <LoyaltyView profile={profile} />;
  }

  return (
    <section className="flex h-full flex-col overflow-hidden rounded-3xl border border-slate-200/60 bg-white/80 p-6 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/70 dark:shadow-[0_45px_95px_-55px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
      {headerContent}
      <div className="mt-5 flex-1 overflow-y-auto pr-1 space-y-6">
        {bodyContent}
        {view === "overview" ? (
          <DestinationIdeasShelf
            destinations={inspirationDestinations}
            uploadError={uploadError}
            onAttachDestination={attachDestinationImage}
            fileInputRef={fileInputRef}
          />
        ) : null}
      </div>
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        className="sr-only"
        onChange={async (event) => {
          const file = event.target.files?.[0];
          if (!file) {
            return;
          }
          await handleCustomUpload(file);
          event.target.value = "";
        }}
      />
    </section>
  );
}

type UploadableImageAttachment = Attachment & {
  upload_url?: string | null;
  preview_url?: string | null;
};

async function uploadImageAttachment(
  chatkit: ChatKitInstance,
  file: File
): Promise<Attachment> {
  const apiConfig = chatkit.control.options.api;
  const apiUrl = "url" in apiConfig ? apiConfig.url : SUPPORT_CHATKIT_API_URL;
  const fileName = file.name || "image-upload";
  const mimeType = file.type || "image/jpeg";

  const createResponse = await fetch(apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type: "attachments.create",
      params: {
        name: fileName,
        size: file.size,
        mime_type: mimeType,
      },
    }),
  });

  if (!createResponse.ok) {
    throw new Error("Unable to register the attachment with ChatKit.");
  }

  const created = (await createResponse.json()) as UploadableImageAttachment;
  const uploadUrl = created.upload_url;

  if (!uploadUrl) {
    return normalizeAttachment(created, fileName, mimeType);
  }

  const formData = new FormData();
  formData.append("file", file);

  const uploadResponse = await fetch(uploadUrl, {
    method: "POST",
    body: formData,
  });

  if (!uploadResponse.ok) {
    throw new Error("Uploading the attachment failed.");
  }

  let saved: UploadableImageAttachment | null = null;
  try {
    saved = (await uploadResponse.json()) as UploadableImageAttachment;
  } catch {
    saved = null;
  }

  const result = saved ?? created;
  return normalizeAttachment(result, fileName, result.mime_type ?? mimeType);
}

function normalizeAttachment(
  input: UploadableImageAttachment,
  fallbackName: string,
  fallbackMimeType: string
): Attachment {
  if (input.type !== "image") {
    throw new Error("Only image attachments are supported.");
  }
  return {
    type: "image",
    id: input.id,
    name: input.name ?? fallbackName,
    mime_type: input.mime_type ?? fallbackMimeType,
    preview_url: input.preview_url ?? "",
  };
}

async function dataUrlToFile(dataUrl: string, filename: string): Promise<File> {
  const response = await fetch(dataUrl);
  const blob = await response.blob();
  const mimeType = blob.type || "image/jpeg";
  return new File([blob], filename, { type: mimeType });
}
