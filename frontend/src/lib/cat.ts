export type CatColorPattern = "black" | "calico" | "colorpoint" | "tabby" | "white";

export type CatStatePayload = {
  threadId?: string | null;
  name: string;
  energy: number;
  happiness: number;
  cleanliness: number;
  age: number;
  colorPattern: CatColorPattern | null;
  updatedAt: string;
};

export type CatSpeechPayload = {
  message: string;
  mood?: string;
};

export const DEFAULT_CAT_STATE: CatStatePayload = {
  threadId: null,
  name: "Unnamed Cat",
  energy: 6,
  happiness: 6,
  cleanliness: 6,
  age: 2,
  colorPattern: null,
  updatedAt: new Date().toISOString(),
};
