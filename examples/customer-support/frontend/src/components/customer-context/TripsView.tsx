import { CalendarDays, Luggage, Utensils } from "lucide-react";

import type { CustomerProfile } from "../../hooks/useCustomerContext";
import { FlightsList } from "./FlightsList";
import { InfoPill } from "./InfoPill";
import { TimelineList } from "./TimelineList";

type TripsViewProps = {
  profile: CustomerProfile;
};

export function TripsView({ profile }: TripsViewProps) {
  return (
    <div className="space-y-6">
      <FlightsList segments={profile.segments} />

      <div className="grid gap-3 sm:grid-cols-3">
        <InfoPill icon={Luggage} label="Checked bags">
          {profile.bags_checked}
        </InfoPill>
        <InfoPill icon={Utensils} label="Meal preference">
          {profile.meal_preference || "Not set"}
        </InfoPill>
        <InfoPill icon={CalendarDays} label="Assistance">
          {profile.special_assistance || "None"}
        </InfoPill>
      </div>

      <TimelineList timeline={profile.timeline} />
    </div>
  );
}

