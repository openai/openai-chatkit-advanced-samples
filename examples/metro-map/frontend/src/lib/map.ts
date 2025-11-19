import { MAP_API_URL } from "./config";

export const X_UNIT = 160;
export const Y_UNIT = 80;

export type Station = {
  id: string;
  name: string;
  x: number;
  y: number;
  description: string;
  lines: string[];
};

export type Line = {
  id: string;
  name: string;
  color: string;
  stations: string[];
};

export type MetroMap = {
  id: string;
  name: string;
  summary: string;
  stations: Station[];
  lines: Line[];
};

export async function fetchMetroMap(): Promise<MetroMap> {
  const response = await fetch(MAP_API_URL);
  if (!response.ok) {
    throw new Error(`Failed to load metro map (${response.status})`);
  }
  const data = (await response.json()) as { map?: MetroMap };
  if (!data.map) {
    throw new Error("Metro map payload missing in response.");
  }
  return data.map;
}

export async function updateMetroMap(map: MetroMap): Promise<MetroMap> {
  const response = await fetch(MAP_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ map }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update metro map (${response.status})`);
  }

  const data = (await response.json()) as { map?: MetroMap };
  if (!data.map) {
    throw new Error("Metro map payload missing in response.");
  }
  return data.map;
}
