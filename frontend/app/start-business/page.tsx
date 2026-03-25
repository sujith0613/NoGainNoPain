"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
  LineChart, Line, PieChart, Pie, Cell,
} from "recharts";

const COLORS = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"];

// ── Sub-components ─────────────────────────────────────────────────────────────
function ScoreCard({ label, value, unit = "", color = "var(--accent)", sub = "" }: {
  label: string; value: number | string; unit?: string; color?: string; sub?: string;
}) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value" style={{ color }}>{value}{unit}</div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  );
}

function SectionBlock({ title, sub, children }: { title: string; sub?: string; children: React.ReactNode }) {
  return (
    <div className="glass-card" style={{ padding: "24px", marginBottom: "20px" }}>
      <div className="section-title">{title}</div>
      {sub && <div className="section-sub">{sub}</div>}
      {children}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function StartBusinessPage() {
  const [cities, setCities] = useState<string[]>([]);
  const [areas, setAreas] = useState<string[]>([]);
  const [cuisines, setCuisines] = useState<string[]>([]);

  const [city, setCity] = useState("");
  const [area, setArea] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [budget, setBudget] = useState(500000);

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    api.cities().then(r => setCities(r.cities || []));
    api.cuisines().then(r => setCuisines(r.cuisines || []));
  }, []);

  useEffect(() => {
    if (city) api.areas(city).then(r => setAreas(r.areas || []));
    else setAreas([]);
  }, [city]);

  async function handleAnalyze() {
    if (!area || !budget) return;
    setLoading(true);
    setData(null);
    try {
      const [rec, pricing, menu, gap, trend, sentiment, peaks, combo, scenario, heatmap] = await Promise.all([
        api.businessRecommendation(area, budget, city),
        cuisine ? api.pricingAnalysis(area, cuisine) : Promise.resolve(null),
        cuisine ? api.menuGeneration(area, cuisine) : Promise.resolve(null),
        api.demandGap(city, area),
        api.trendAnalysis(city, cuisine),
        api.sentimentAnalysis(area, cuisine),
        api.peakHours(area, cuisine),
        cuisine ? api.comboAnalysis(cuisine, area) : Promise.resolve(null),
        cuisine ? api.scenarioSimulation(area, cuisine, budget) : Promise.resolve(null),
        api.heatmapData(city),
      ]);
      setData({ rec, pricing, menu, gap, trend, sentiment, peaks, combo, scenario, heatmap });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const TABS = ["Overview", "Pricing & Menu", "Demand & Trends", "Sentiment", "Peak Hours", "Scenario"];

  return (
    <div style={{ padding: "40px 0 80px" }}>
      <div className="container">
        {/* Header */}
        <div style={{ marginBottom: "36px" }}>
          <h1 style={{ fontSize: "36px", fontWeight: 800, marginBottom: "8px" }}>
            🚀 Start a Business
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>
            Enter your target area and budget to get AI-powered market intelligence
          </p>
        </div>

        {/* Input Form */}
        <div className="glass-card" style={{ padding: "28px", marginBottom: "28px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px", alignItems: "end" }}>
            <div>
              <label className="form-label">City</label>
              <select className="form-select" value={city} onChange={e => { setCity(e.target.value); setArea(""); }}>
                <option value="">All Cities</option>
                {cities.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="form-label">Area *</label>
              <select className="form-select" value={area} onChange={e => setArea(e.target.value)}>
                <option value="">Select Area</option>
                {areas.map(a => <option key={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="form-label">Cuisine (optional)</label>
              <select className="form-select" value={cuisine} onChange={e => setCuisine(e.target.value)}>
                <option value="">Any Cuisine</option>
                {cuisines.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="form-label">Budget (₹)</label>
              <input className="form-input" type="number" value={budget}
                onChange={e => setBudget(Number(e.target.value))} min={100000} step={50000} />
            </div>
            <button className="btn-primary" onClick={handleAnalyze} disabled={loading || !area}>
              {loading ? "Analyzing…" : "🔍 Analyze Market"}
            </button>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: "center", padding: "60px 0" }}>
            <div className="spinner" />
            <p style={{ color: "var(--text-secondary)", marginTop: "16px" }}>Running 10 intelligence modules…</p>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <>
            {/* Top Score Cards */}
            <div className="metrics-grid cols-4" style={{ marginBottom: "24px" }}>
              {(data.rec as any)?.top_recommendations?.[0] && (() => {
                const top = (data.rec as any).top_recommendations[0];
                return (
                  <>
                    <ScoreCard label="Opportunity Score" value={(top.opportunity_score * 1000).toFixed(2)} color="var(--success)" sub="Top cuisine" />
                    <ScoreCard label="Risk Score" value={(top.risk_score * 100).toFixed(1)} unit="%" color="var(--warning)" sub="Market risk" />
                    <ScoreCard label="Demand Score" value={(top.demand_score * 100).toFixed(1)} unit="%" color="var(--accent)" sub="Market demand" />
                    <ScoreCard label="Suggested Type" value={top.suggested_business_type} color="var(--accent-3)" sub={top.cuisine_type} />
                  </>
                );
              })()}
            </div>

            {/* AI Summary */}
            {(data.rec as any)?.ai_summary && (
              <div className="ai-summary" style={{ marginBottom: "24px" }}>
                🤖 <strong>AI Insight:</strong> {(data.rec as any).ai_summary}
              </div>
            )}

            {/* Tabs */}
            <div className="tabs">
              {TABS.map((t, i) => (
                <button key={t} className={`tab-btn ${activeTab === i ? "active" : ""}`} onClick={() => setActiveTab(i)}>{t}</button>
              ))}
            </div>

            {/* Tab 0: Overview */}
            {activeTab === 0 && (
              <>
                <SectionBlock title="Top Cuisine Recommendations" sub={`Best business opportunities in ${area}`}>
                  {(data.rec as any)?.top_recommendations?.length > 0 ? (
                    <div style={{ overflowX: "auto" }}>
                      <table className="data-table">
                        <thead><tr>
                          <th>Cuisine</th><th>Business Type</th><th>Opportunity</th>
                          <th>Risk</th><th>Demand</th><th>Avg Price</th><th>Growth</th>
                        </tr></thead>
                        <tbody>
                          {(data.rec as any).top_recommendations.map((r: any, i: number) => (
                            <tr key={i}>
                              <td><strong>{r.cuisine_type}</strong></td>
                              <td><span className="tag tag-new">{r.suggested_business_type}</span></td>
                              <td><span className={`score-badge ${r.opportunity_score > 0.001 ? "high" : "medium"}`}>
                                {(r.opportunity_score * 1000).toFixed(2)}
                              </span></td>
                              <td><span className={`score-badge ${r.risk_score < 0.4 ? "high" : r.risk_score < 0.6 ? "medium" : "low"}`}>
                                {(r.risk_score * 100).toFixed(1)}%
                              </span></td>
                              <td>{(r.demand_score * 100).toFixed(1)}%</td>
                              <td>₹{r.avg_competitor_price?.toFixed(0)}</td>
                              <td style={{ color: r.review_growth_rate >= 0 ? "var(--success)" : "var(--danger)" }}>
                                {r.review_growth_rate >= 0 ? "↑" : "↓"} {Math.abs(r.review_growth_rate * 100).toFixed(1)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : <p style={{ color: "var(--text-muted)" }}>No recommendations available.</p>}
                </SectionBlock>

                {/* Demand Gap */}
                <SectionBlock title="Demand-Supply Gaps" sub="High demand, low competition opportunities">
                  {(data.gap as any)?.gaps?.length > 0 ? (
                    <>
                      <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={(data.gap as any).gaps.slice(0, 8)} margin={{ top: 5, right: 20, left: 0, bottom: 60 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                          <XAxis dataKey="dish_name" tick={{ fill: "#9ca3af", fontSize: 11 }} angle={-35} textAnchor="end" />
                          <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
                          <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} />
                          <Legend wrapperStyle={{ color: "#9ca3af", fontSize: 12 }} />
                          <Bar dataKey="demand_score" name="Demand Score" fill="#6366f1" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="supply_count" name="Supply Count" fill="#ef4444" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                      <div className="ai-summary" style={{ marginTop: 16 }}>
                        🤖 {(data.gap as any).ai_summary}
                      </div>
                    </>
                  ) : <p style={{ color: "var(--text-muted)" }}>No gap data available.</p>}
                </SectionBlock>
              </>
            )}

            {/* Tab 1: Pricing & Menu */}
            {activeTab === 1 && (
              <>
                {(data.pricing as any)?.dishes?.length > 0 ? (
                  <SectionBlock title="Pricing Intelligence" sub={`Optimal pricing for ${cuisine} in ${area}`}>
                    <div style={{ marginBottom: 16 }} className="ai-summary">
                      🤖 {(data.pricing as any).ai_summary}
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={(data.pricing as any).dishes.slice(0, 8)} margin={{ top: 5, right: 20, left: 0, bottom: 70 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                        <XAxis dataKey="dish_name" tick={{ fill: "#9ca3af", fontSize: 11 }} angle={-40} textAnchor="end" />
                        <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
                        <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} formatter={(v: number) => `₹${v}`} />
                        <Legend wrapperStyle={{ color: "#9ca3af", fontSize: 12 }} />
                        <Bar dataKey="avg_price" name="Your Avg Price" fill="#6366f1" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="competitor_avg_price" name="Market Avg" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="optimal_price" name="Optimal Price" fill="#10b981" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                    <div style={{ overflowX: "auto", marginTop: 20 }}>
                      <table className="data-table">
                        <thead><tr><th>Dish</th><th>Avg Price</th><th>Optimal Price</th><th>Deviation</th><th>Action</th></tr></thead>
                        <tbody>
                          {(data.pricing as any).dishes.map((d: any, i: number) => (
                            <tr key={i}>
                              <td><strong>{d.dish_name}</strong></td>
                              <td>₹{d.avg_price}</td>
                              <td style={{ color: "var(--success)" }}>₹{d.optimal_price}</td>
                              <td style={{ color: d.price_deviation > 0 ? "var(--danger)" : "var(--success)" }}>
                                {d.price_deviation > 0 ? "+" : ""}{(d.price_deviation * 100).toFixed(1)}%
                              </td>
                              <td style={{ fontSize: 12, color: "var(--text-secondary)" }}>{d.pricing_action}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </SectionBlock>
                ) : <div className="glass-card" style={{ padding: 24 }}><p style={{ color: "var(--text-muted)" }}>Select a cuisine to see pricing analysis.</p></div>}

                {(data.menu as any)?.dishes?.length > 0 ? (
                  <SectionBlock title="Recommended Menu" sub="Top dishes by demand × rating × sentiment">
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 14 }}>
                      {(data.menu as any).dishes.map((d: any, i: number) => (
                        <div key={i} style={{ padding: "14px 16px", border: "1px solid var(--border)", borderRadius: 12, background: "var(--bg-glass)" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                            <strong style={{ fontSize: 14 }}>{d.dish_name}</strong>
                            <span className={`tag ${d.is_veg ? "tag-veg" : "tag-nveg"}`}>{d.is_veg ? "🟢 Veg" : "🔴 Non-Veg"}</span>
                          </div>
                          <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8 }}>{d.dish_category}</div>
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                            <span style={{ color: "var(--success)" }}>₹{d.avg_price?.toFixed(0)}</span>
                            <span style={{ color: "var(--accent)" }}>⭐ {d.avg_rating?.toFixed(1)}</span>
                          </div>
                          <div className="progress-bar" style={{ marginTop: 8 }}>
                            <div className="progress-bar-fill" style={{ width: `${d.menu_score * 100}%` }} />
                          </div>
                          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                            Menu Score: {(d.menu_score * 100).toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </SectionBlock>
                ) : null}

                {(data.combo as any)?.combos?.length > 0 ? (
                  <SectionBlock title="Combo Recommendations" sub="High-association dish bundles">
                    <div style={{ overflowX: "auto" }}>
                      <table className="data-table">
                        <thead><tr><th>#</th><th>Dish A</th><th>Dish B</th><th>Association</th><th>Bundle Price</th></tr></thead>
                        <tbody>
                          {(data.combo as any).combos.slice(0, 8).map((c: any, i: number) => (
                            <tr key={i}>
                              <td style={{ color: "var(--text-muted)" }}>#{i + 1}</td>
                              <td>{c.dish_a}</td>
                              <td>{c.dish_b}</td>
                              <td>
                                <div className="progress-bar" style={{ width: 80 }}>
                                  <div className="progress-bar-fill" style={{ width: `${c.combo_score * 100}%` }} />
                                </div>
                              </td>
                              <td style={{ color: "var(--success)" }}>
                                {c.suggested_price_bundle ? `₹${c.suggested_price_bundle}` : "—"}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </SectionBlock>
                ) : null}
              </>
            )}

            {/* Tab 2: Demand & Trends */}
            {activeTab === 2 && (
              <>
                <SectionBlock title="Cuisine Trends" sub="Rising and declining cuisines by growth rate">
                  <div className="grid-2" style={{ gap: 20 }}>
                    <div>
                      <h4 style={{ color: "var(--success)", marginBottom: 12, fontSize: 14 }}>🚀 Rising Cuisines</h4>
                      {(data.trend as any)?.rising_cuisines?.map((r: any, i: number) => (
                        <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
                          <div>
                            <div style={{ fontSize: 14, fontWeight: 600 }}>{r.cuisine_type}</div>
                            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>⭐ {r.avg_rating?.toFixed(1)} avg rating</div>
                          </div>
                          <span className="score-badge high">↑ {(r.trend_score * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <h4 style={{ color: "var(--danger)", marginBottom: 12, fontSize: 14 }}>📉 Declining Cuisines</h4>
                      {(data.trend as any)?.declining_cuisines?.map((r: any, i: number) => (
                        <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
                          <div style={{ fontSize: 14, fontWeight: 600 }}>{r.cuisine_type}</div>
                          <span className="score-badge low">↓ {Math.abs(r.trend_score * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {(data.trend as any)?.rising_cuisines?.length > 0 && (
                    <ResponsiveContainer width="100%" height={220} style={{ marginTop: 24 }}>
                      <BarChart data={(data.trend as any).rising_cuisines} margin={{ top: 0, right: 20, left: 0, bottom: 40 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                        <XAxis dataKey="cuisine_type" tick={{ fill: "#9ca3af", fontSize: 11 }} angle={-30} textAnchor="end" />
                        <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
                        <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} />
                        <Bar dataKey="trend_score" name="Trend Score" fill="#10b981" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="demand_growth" name="Demand Growth" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </SectionBlock>

                {(data.trend as any)?.trending_dishes?.length > 0 && (
                  <SectionBlock title="Trending Dishes" sub="Top dishes by demand growth">
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                      {(data.trend as any).trending_dishes.map((d: any, i: number) => (
                        <div key={i} style={{ padding: "8px 14px", borderRadius: 10, background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.25)" }}>
                          <span style={{ fontSize: 13, fontWeight: 600 }}>{d.dish_name}</span>
                          {d.is_new && <span className="tag tag-new" style={{ marginLeft: 6 }}>NEW</span>}
                          <span style={{ marginLeft: 10, fontSize: 12, color: "var(--success)" }}>↑ {(d.demand_growth * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </SectionBlock>
                )}
              </>
            )}

            {/* Tab 3: Sentiment */}
            {activeTab === 3 && (data.sentiment as any) && (
              <SectionBlock title="Sentiment Analysis" sub="Aspect-level sentiment breakdown">
                <div className="metrics-grid cols-3" style={{ marginBottom: 24 }}>
                  {Object.entries((data.sentiment as any).aspects || {}).map(([key, val]: [string, any]) => (
                    <ScoreCard key={key} label={key.charAt(0).toUpperCase() + key.slice(1)}
                      value={(val.score * 100).toFixed(1)} unit="%" sub={val.label}
                      color={val.label === "positive" ? "var(--success)" : val.label === "negative" ? "var(--danger)" : "var(--warning)"} />
                  ))}
                </div>
                <div className="grid-2">
                  <div>
                    <h4 style={{ fontSize: 14, marginBottom: 12, color: "var(--text-secondary)" }}>Sentiment Distribution</h4>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie data={Object.entries((data.sentiment as any).sentiment_distribution || {}).map(([k, v]) => ({ name: k, value: v as number }))}
                          cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                          {["#10b981", "#f59e0b", "#ef4444"].map((c, i) => <Cell key={i} fill={c} />)}
                        </Pie>
                        <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div>
                    <h4 style={{ fontSize: 14, marginBottom: 12, color: "var(--text-secondary)" }}>By Cuisine Type</h4>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={(data.sentiment as any).by_cuisine?.slice(0, 6) || []} layout="vertical" margin={{ left: 80 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                        <XAxis type="number" domain={[-1, 1]} tick={{ fill: "#9ca3af", fontSize: 11 }} />
                        <YAxis type="category" dataKey="cuisine_type" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                        <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} />
                        <Bar dataKey="sentiment" fill="#6366f1" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                <div className="ai-summary" style={{ marginTop: 16 }}>🤖 {(data.sentiment as any).ai_summary}</div>
              </SectionBlock>
            )}

            {/* Tab 4: Peak Hours */}
            {activeTab === 4 && (data.peaks as any)?.hours?.length > 0 && (
              <SectionBlock title="Peak Hour Analysis" sub="Demand distribution across the day">
                <div style={{ marginBottom: 12 }}>
                  <strong>Peak Hours:</strong>{" "}
                  {(data.peaks as any).peak_hours?.map((h: string) => (
                    <span key={h} className="score-badge high" style={{ marginRight: 6 }}>{h}</span>
                  ))}
                </div>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={(data.peaks as any).hours} margin={{ top: 5, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="label" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                    <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
                    <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} />
                    <Legend wrapperStyle={{ color: "#9ca3af", fontSize: 12 }} />
                    <Bar dataKey="demand_pct" name="Demand %" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="avg_rating" name="Avg Rating" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
                <div className="ai-summary" style={{ marginTop: 16 }}>🤖 {(data.peaks as any).ai_summary}</div>
              </SectionBlock>
            )}

            {/* Tab 5: Scenario */}
            {activeTab === 5 && (data.scenario as any) && (
              <SectionBlock title="Scenario Simulation" sub={`Impact of opening a new ${cuisine} restaurant in ${area}`}>
                <div className="metrics-grid cols-4" style={{ marginBottom: 24 }}>
                  <ScoreCard label="Viability" value={(data.scenario as any).viability}
                    color={(data.scenario as any).viability === "Viable" ? "var(--success)" : "var(--danger)"} />
                  <ScoreCard label="ROI Timeline" value={(data.scenario as any).roi_months} unit=" months" color="var(--warning)" />
                  <ScoreCard label="Est. Monthly Revenue" value={"₹" + ((data.scenario as any).estimated_monthly_revenue / 1000).toFixed(0) + "K"} color="var(--accent)" />
                  <ScoreCard label="Competition Impact" value={((data.scenario as any).delta?.competition_impact * 100).toFixed(1)} unit="%" color="var(--danger)" sub="Increase" />
                </div>
                <div className="grid-2">
                  <div className="metric-card">
                    <div className="metric-label">Before Entry</div>
                    <div style={{ marginTop: 12, fontSize: 14 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Opportunity Score</span>
                        <strong>{((data.scenario as any).before?.opportunity_score * 1000).toFixed(3)}</strong>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Supply Count</span>
                        <strong>{(data.scenario as any).before?.supply_count}</strong>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Competition</span>
                        <strong>{((data.scenario as any).before?.competition_density * 100).toFixed(1)}%</strong>
                      </div>
                    </div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-label">After Entry</div>
                    <div style={{ marginTop: 12, fontSize: 14 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Opportunity Score</span>
                        <strong style={{ color: "var(--warning)" }}>{((data.scenario as any).after?.opportunity_score * 1000).toFixed(3)}</strong>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Supply Count</span>
                        <strong style={{ color: "var(--danger)" }}>{(data.scenario as any).after?.supply_count}</strong>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Competition</span>
                        <strong style={{ color: "var(--danger)" }}>{((data.scenario as any).after?.competition_density * 100).toFixed(1)}%</strong>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="ai-summary" style={{ marginTop: 16 }}>🤖 {(data.scenario as any).ai_summary}</div>
              </SectionBlock>
            )}
          </>
        )}
      </div>
    </div>
  );
}
