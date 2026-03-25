"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from "recharts";

function ScoreGauge({ value, label, color }: { value: number; label: string; color: string }) {
  const pct = Math.min(Math.max(value * 100, 0), 100);
  const r = 54;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <div style={{ textAlign: "center" }}>
      <svg width="130" height="130" viewBox="0 0 130 130" style={{ display: "block", margin: "0 auto" }}>
        <circle cx="65" cy="65" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="12" />
        <circle cx="65" cy="65" r={r} fill="none" stroke={color} strokeWidth="12"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          transform="rotate(-90 65 65)" style={{ transition: "stroke-dasharray 1s ease" }} />
        <text x="65" y="62" textAnchor="middle" fill="#f9fafb" fontSize="20" fontWeight="800">{pct.toFixed(0)}</text>
        <text x="65" y="78" textAnchor="middle" fill="#9ca3af" fontSize="10">/ 100</text>
      </svg>
      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginTop: 4 }}>{label}</div>
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

export default function ImproveBusinessPage() {
  const [restaurants, setRestaurants] = useState<any[]>([]);
  const [areas, setAreas] = useState<string[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [filterArea, setFilterArea] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    api.areas().then(r => setAreas(r.areas || []));
  }, []);

  useEffect(() => {
    api.restaurants(filterArea).then(r => setRestaurants(r.restaurants || []));
  }, [filterArea]);

  async function handleAnalyze() {
    if (!selectedId) return;
    setLoading(true);
    setData(null);
    try {
      const [competitor, performance, improvements, gaps] = await Promise.all([
        api.competitorAnalysis("", selectedId),
        api.performanceScore("", selectedId),
        api.improvementRecommendations("", selectedId),
        api.gapAnalysis("", selectedId),
      ]);
      setData({ competitor, performance, improvements, gaps });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const TABS = ["Overview", "Competitor Compare", "Improvements", "Gap Analysis"];

  return (
    <div style={{ padding: "40px 0 80px" }}>
      <div className="container">
        {/* Header */}
        <div style={{ marginBottom: "36px" }}>
          <h1 style={{ fontSize: "36px", fontWeight: 800, marginBottom: "8px" }}>📈 Improve My Business</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>
            Select your restaurant to get competitor intelligence and improvement recommendations
          </p>
        </div>

        {/* Input Form */}
        <div className="glass-card" style={{ padding: "28px", marginBottom: "28px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", alignItems: "end" }}>
            <div>
              <label className="form-label">Filter by Area</label>
              <select className="form-select" value={filterArea} onChange={e => setFilterArea(e.target.value)}>
                <option value="">All Areas</option>
                {areas.map(a => <option key={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="form-label">Select Restaurant *</label>
              <select className="form-select" value={selectedId} onChange={e => setSelectedId(e.target.value)}>
                <option value="">Choose a restaurant...</option>
                {restaurants.map((r: any) => (
                  <option key={r.restaurant_id} value={r.restaurant_id}>
                    {r.restaurant_name} — {r.area} ({r.cuisine_type})
                  </option>
                ))}
              </select>
            </div>
            <button className="btn-primary" onClick={handleAnalyze} disabled={loading || !selectedId}>
              {loading ? "Analyzing…" : "🔍 Analyze"}
            </button>
          </div>
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: "60px 0" }}>
            <div className="spinner" />
            <p style={{ color: "var(--text-secondary)", marginTop: "16px" }}>Running competitor intelligence…</p>
          </div>
        )}

        {data && !loading && (
          <>
            {/* Performance Score Gauges */}
            <div className="glass-card" style={{ padding: "32px", marginBottom: "24px" }}>
              <div className="section-title" style={{ marginBottom: 24 }}>Performance Overview</div>
              <div style={{ display: "flex", justifyContent: "space-around", flexWrap: "wrap", gap: 24 }}>
                <ScoreGauge value={(data.performance as any)?.performance_score || 0} label="Performance Score" color="var(--accent)" />
                <ScoreGauge value={(data.performance as any)?.breakdown?.rating || 0} label="Rating" color="var(--success)" />
                <ScoreGauge value={(data.performance as any)?.breakdown?.taste || 0} label="Taste" color="#f59e0b" />
                <ScoreGauge value={(data.performance as any)?.breakdown?.service || 0} label="Service" color="var(--accent-3)" />
                <ScoreGauge value={Math.max(((data.performance as any)?.breakdown?.growth + 1) / 2 || 0.5, 0)} label="Growth" color="#8b5cf6" />
              </div>

              <div style={{ display: "flex", justifyContent: "center", gap: 40, marginTop: 32, flexWrap: "wrap" }}>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: 800, color: "var(--accent)" }}>
                    #{(data.performance as any)?.rank_in_area}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    of {(data.performance as any)?.total_competitors} in area
                  </div>
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: 800, color: "var(--success)" }}>
                    {(data.performance as any)?.percentile_rank}%
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Percentile Rank</div>
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text-primary)" }}>
                    {(data.performance as any)?.restaurant_name}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    {(data.performance as any)?.area} · {(data.performance as any)?.cuisine_type}
                  </div>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
              {TABS.map((t, i) => (
                <button key={t} className={`tab-btn ${activeTab === i ? "active" : ""}`} onClick={() => setActiveTab(i)}>{t}</button>
              ))}
            </div>

            {/* Tab 0: Overview */}
            {activeTab === 0 && (
              <SectionBlock title="Top Competitors" sub={`Other ${(data.competitor as any)?.cuisine_type} restaurants in ${(data.competitor as any)?.area}`}>
                {(data.competitor as any)?.top_competitors?.length > 0 ? (
                  <div style={{ overflowX: "auto" }}>
                    <table className="data-table">
                      <thead><tr>
                        <th>Restaurant</th><th>Avg Rating</th><th>Avg Price</th>
                        <th>Demand</th><th>Sentiment</th><th>Performance</th>
                      </tr></thead>
                      <tbody>
                        {(data.competitor as any).top_competitors.map((c: any, i: number) => (
                          <tr key={i}>
                            <td><strong>{c.name}</strong></td>
                            <td>⭐ {c.avg_rating}</td>
                            <td>₹{c.avg_price?.toFixed(0)}</td>
                            <td>
                              <div className="progress-bar" style={{ width: 80 }}>
                                <div className="progress-bar-fill" style={{ width: `${c.demand_score * 100}%` }} />
                              </div>
                            </td>
                            <td style={{ color: c.sentiment_score > 0 ? "var(--success)" : "var(--danger)" }}>
                              {c.sentiment_score > 0 ? "😊" : "😞"} {c.sentiment_score?.toFixed(3)}
                            </td>
                            <td>
                              <span className={`score-badge ${c.performance_score > 0.6 ? "high" : c.performance_score > 0.4 ? "medium" : "low"}`}>
                                {(c.performance_score * 100).toFixed(1)}%
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : <p style={{ color: "var(--text-muted)" }}>No competitors found in same area.</p>}
              </SectionBlock>
            )}

            {/* Tab 1: Competitor Compare */}
            {activeTab === 1 && (data.competitor as any)?.target_metrics && (
              <SectionBlock title="You vs. Competitors" sub="Head-to-head comparison on key metrics">
                <ResponsiveContainer width="100%" height={320}>
                  <RadarChart data={[
                    { metric: "Rating", you: ((data.competitor as any).target_metrics.normalized_rating || 0) * 100, competitor: ((data.competitor as any).competitor_metrics.rating / 5 || 0) * 100 },
                    { metric: "Demand", you: ((data.competitor as any).target_metrics.demand_score || 0) * 100, competitor: ((data.competitor as any).competitor_metrics.demand_score || 0) * 100 },
                    { metric: "Sentiment", you: (((data.competitor as any).target_metrics.sentiment_score + 1) / 2) * 100, competitor: (((data.competitor as any).competitor_metrics.sentiment_score + 1) / 2) * 100 },
                    { metric: "Taste", you: ((data.competitor as any).target_metrics.taste_score || 0) * 100, competitor: ((data.competitor as any).competitor_metrics.taste_score || 0) * 100 },
                    { metric: "Service", you: ((data.competitor as any).target_metrics.service_score || 0) * 100, competitor: ((data.competitor as any).competitor_metrics.service_score || 0) * 100 },
                    { metric: "Growth", you: (((data.competitor as any).target_metrics.demand_growth_rate + 1) / 2) * 100, competitor: (((data.competitor as any).competitor_metrics.demand_growth_rate + 1) / 2) * 100 },
                  ]}>
                    <PolarGrid stroke="rgba(255,255,255,0.08)" />
                    <PolarAngleAxis dataKey="metric" tick={{ fill: "#9ca3af", fontSize: 12 }} />
                    <Radar name="You" dataKey="you" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                    <Radar name="Competitors" dataKey="competitor" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
                    <Legend wrapperStyle={{ color: "#9ca3af", fontSize: 12 }} />
                    <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} formatter={(v: number) => `${v.toFixed(1)}%`} />
                  </RadarChart>
                </ResponsiveContainer>

                {/* Comparison Table */}
                <div style={{ overflowX: "auto", marginTop: 20 }}>
                  <table className="data-table">
                    <thead><tr><th>Metric</th><th>You</th><th>Competitor Avg</th><th>Gap</th></tr></thead>
                    <tbody>
                      {[
                        { label: "Rating", you: (data.competitor as any)?.target_metrics?.rating?.toFixed(2), comp: (data.competitor as any)?.competitor_metrics?.rating?.toFixed(2), key: "rating" },
                        { label: "Demand Score", you: ((data.competitor as any)?.target_metrics?.demand_score * 100)?.toFixed(1) + "%", comp: ((data.competitor as any)?.competitor_metrics?.demand_score * 100)?.toFixed(1) + "%", key: "demand_score" },
                        { label: "Avg Price (₹)", you: (data.competitor as any)?.target_metrics?.dish_price?.toFixed(0), comp: (data.competitor as any)?.competitor_metrics?.dish_price?.toFixed(0), key: "dish_price" },
                        { label: "Taste Score", you: ((data.competitor as any)?.target_metrics?.taste_score * 100)?.toFixed(1) + "%", comp: ((data.competitor as any)?.competitor_metrics?.taste_score * 100)?.toFixed(1) + "%", key: "taste_score" },
                        { label: "Service Score", you: ((data.competitor as any)?.target_metrics?.service_score * 100)?.toFixed(1) + "%", comp: ((data.competitor as any)?.competitor_metrics?.service_score * 100)?.toFixed(1) + "%", key: "service_score" },
                      ].map(row => {
                        const youNum = parseFloat(String(row.you));
                        const compNum = parseFloat(String(row.comp));
                        const better = row.key === "dish_price" ? youNum <= compNum : youNum >= compNum;
                        return (
                          <tr key={row.label}>
                            <td>{row.label}</td>
                            <td style={{ color: better ? "var(--success)" : "var(--danger)", fontWeight: 600 }}>{row.you}</td>
                            <td style={{ color: "var(--text-secondary)" }}>{row.comp}</td>
                            <td>
                              <span className={`score-badge ${better ? "high" : "low"}`}>
                                {better ? "✅ Better" : "⚠️ Below"}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </SectionBlock>
            )}

            {/* Tab 2: Improvements */}
            {activeTab === 2 && (
              <SectionBlock title="Improvement Recommendations" sub="Prioritized action plan for your restaurant">
                {(data.improvements as any)?.ai_summary && (
                  <div className="ai-summary" style={{ marginBottom: 20 }}>
                    🤖 <strong>Top Priority:</strong> {(data.improvements as any).ai_summary}
                  </div>
                )}
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {(data.improvements as any)?.recommendations?.map((r: any, i: number) => (
                    <div key={i} className="rec-card">
                      <div className="rec-priority">{r.priority}</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                          <span className="rec-area">{r.area}</span>
                          <span className={`score-badge ${r.impact === "High" ? "low" : r.impact === "Medium" ? "medium" : "high"}`}
                            style={{ fontSize: 11 }}>{r.impact} Impact</span>
                        </div>
                        <div style={{ fontSize: 13, color: "var(--warning)", marginBottom: 4 }}>💡 {r.insight}</div>
                        <div className="rec-action">{r.action}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </SectionBlock>
            )}

            {/* Tab 3: Gap Analysis */}
            {activeTab === 3 && (
              <>
                <SectionBlock title="Missing Dishes" sub="Popular dishes offered by competitors but not you">
                  {(data.gaps as any)?.missing_dishes?.length > 0 ? (
                    <div style={{ overflowX: "auto" }}>
                      <table className="data-table">
                        <thead><tr>
                          <th>Dish Name</th><th>Competitor Demand</th><th>Avg Price</th><th>Offered By</th>
                        </tr></thead>
                        <tbody>
                          {(data.gaps as any).missing_dishes.map((d: any, i: number) => (
                            <tr key={i}>
                              <td><strong>{d.dish_name}</strong></td>
                              <td>
                                <div className="progress-bar" style={{ width: 100 }}>
                                  <div className="progress-bar-fill" style={{ width: `${d.competitor_avg_demand * 100}%` }} />
                                </div>
                              </td>
                              <td>₹{d.competitor_avg_price}</td>
                              <td>{d.offered_by_n_competitors} competitors</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : <p style={{ color: "var(--success)" }}>✅ No significant missing dishes!</p>}
                </SectionBlock>

                <SectionBlock title="Weak Sentiment Areas" sub="Aspects where you underperform versus competitors">
                  {(data.gaps as any)?.weak_sentiment_areas?.length > 0 ? (
                    <>
                      <ResponsiveContainer width="100%" height={220}>
                        <BarChart data={(data.gaps as any).weak_sentiment_areas} layout="vertical" margin={{ left: 80 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                          <XAxis type="number" domain={[0, 1]} tick={{ fill: "#9ca3af", fontSize: 11 }} />
                          <YAxis type="category" dataKey="aspect" tick={{ fill: "#9ca3af", fontSize: 12 }} />
                          <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)" }} />
                          <Legend wrapperStyle={{ color: "#9ca3af", fontSize: 12 }} />
                          <Bar dataKey="my_score" name="Your Score" fill="#ef4444" radius={[0, 4, 4, 0]} />
                          <Bar dataKey="competitor_avg" name="Competitor Avg" fill="#10b981" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                      <div style={{ marginTop: 16 }}>
                        {(data.gaps as any).weak_sentiment_areas.map((a: any, i: number) => (
                          <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
                            <span style={{ textTransform: "capitalize", fontWeight: 600 }}>{a.aspect}</span>
                            <div style={{ display: "flex", gap: 16 }}>
                              <span style={{ color: "var(--danger)" }}>You: {(a.my_score * 100).toFixed(1)}%</span>
                              <span style={{ color: "var(--success)" }}>Avg: {(a.competitor_avg * 100).toFixed(1)}%</span>
                              <span className="score-badge low">Gap: {(a.gap * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : <p style={{ color: "var(--success)" }}>✅ No significant sentiment gaps detected!</p>}

                  <div className="ai-summary" style={{ marginTop: 16 }}>🤖 {(data.gaps as any)?.ai_summary}</div>
                </SectionBlock>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
