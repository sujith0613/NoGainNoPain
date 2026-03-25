const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function apiFetch(path: string, params: Record<string, string | number> = {}) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== "" && v !== undefined) url.searchParams.set(k, String(v));
  });
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  // Metadata
  cities: () => apiFetch("/cities"),
  areas: (city = "") => apiFetch("/areas", { city }),
  cuisines: () => apiFetch("/cuisines"),
  restaurants: (area = "", city = "") => apiFetch("/restaurants", { area, city }),

  // Market Intelligence
  businessRecommendation: (area: string, budget: number, city = "") =>
    apiFetch("/business-recommendation", { area, budget, city }),
  pricingAnalysis: (area: string, cuisine_type: string) =>
    apiFetch("/pricing-analysis", { area, cuisine_type }),
  menuGeneration: (area: string, cuisine_type: string, top_n = 10) =>
    apiFetch("/menu-generation", { area, cuisine_type, top_n }),
  demandGap: (city = "", area = "") =>
    apiFetch("/demand-gap", { city, area }),
  trendAnalysis: (city = "", cuisine_type = "") =>
    apiFetch("/trend-analysis", { city, cuisine_type }),
  sentimentAnalysis: (area = "", cuisine_type = "") =>
    apiFetch("/sentiment-analysis", { area, cuisine_type }),
  peakHours: (area = "", cuisine_type = "") =>
    apiFetch("/peak-hours", { area, cuisine_type }),
  comboAnalysis: (cuisine_type = "", area = "") =>
    apiFetch("/combo-analysis", { cuisine_type, area }),
  scenarioSimulation: (area: string, cuisine_type: string, budget: number) =>
    apiFetch("/scenario-simulation", { area, cuisine_type, budget }),
  heatmapData: (city = "") =>
    apiFetch("/heatmap-data", { city }),

  // Competitor
  competitorAnalysis: (restaurant_name = "", restaurant_id = "", area = "", cuisine_type = "") =>
    apiFetch("/competitor-analysis", { restaurant_name, restaurant_id, area, cuisine_type }),
  performanceScore: (restaurant_name = "", restaurant_id = "") =>
    apiFetch("/performance-score", { restaurant_name, restaurant_id }),
  improvementRecommendations: (restaurant_name = "", restaurant_id = "") =>
    apiFetch("/improvement-recommendations", { restaurant_name, restaurant_id }),
  gapAnalysis: (restaurant_name = "", restaurant_id = "") =>
    apiFetch("/gap-analysis", { restaurant_name, restaurant_id }),
};
