export type GarmentTag = {
  name: string;
  color: string;
  fabric: string;
  formality: "casual" | "smart-casual" | "formal";
  subcategory: "top" | "bottom" | "layer" | "shoes" | "dress";
};

export type OutfitSuggestion = {
  id: string;
  title: string;
  pieces: GarmentTag[];
  reason: string;
  vibeScore: number;
};
