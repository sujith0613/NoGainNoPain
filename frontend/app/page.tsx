export default function HomePage() {
  return (
    <div style={{ padding: "0 0 80px" }}>
      {/* Hero Section */}
      <section style={{
        minHeight: "88vh", display: "flex", alignItems: "center", justifyContent: "center",
        position: "relative", overflow: "hidden", textAlign: "center",
      }}>
        {/* Background glows */}
        <div style={{
          position: "absolute", width: "600px", height: "600px",
          borderRadius: "50%", background: "radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)",
          top: "-100px", left: "-100px", pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", width: "500px", height: "500px",
          borderRadius: "50%", background: "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)",
          bottom: "-50px", right: "-50px", pointerEvents: "none",
        }} />

        <div className="container" style={{ position: "relative", zIndex: 1 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "8px",
            padding: "6px 16px", borderRadius: "20px", border: "1px solid rgba(99,102,241,0.3)",
            background: "rgba(99,102,241,0.08)", fontSize: "13px", color: "var(--accent)",
            marginBottom: "28px", fontWeight: 500,
          }}>
            AI-Powered • Real-time Intelligence • Decision Engine
          </div>

          <h1 style={{
            fontSize: "clamp(40px, 7vw, 72px)", fontWeight: 900, lineHeight: 1.1,
            marginBottom: "24px", letterSpacing: "-1px",
          }}>
            <span style={{ background: "var(--gradient-hero)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              Food Market Intelligence
            </span>
            <br />
            <span style={{ color: "var(--text-primary)" }}>& Decision Engine</span>
          </h1>

          <p style={{ fontSize: "18px", color: "var(--text-secondary)", maxWidth: "600px", margin: "0 auto 40px", lineHeight: 1.7 }}>
            Transform raw food market data into actionable decisions. Whether you&apos;re starting
            a new food business or optimizing an existing one — FoodIQ has you covered.
          </p>

          <div style={{ display: "flex", gap: "16px", justifyContent: "center", flexWrap: "wrap" }}>
            <a href="/start-business">
              <button className="btn-primary" style={{ fontSize: "16px", padding: "14px 32px" }}>
                Start a Business
              </button>
            </a>
            <a href="/improve-business">
              <button className="btn-secondary" style={{ fontSize: "16px", padding: "14px 32px" }}>
                Improve My Business
              </button>
            </a>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="container">
        <div style={{ textAlign: "center", marginBottom: "48px" }}>
          <h2 className="section-title" style={{ fontSize: "32px" }}>Everything you need to decide smarter</h2>
          <p className="section-sub">14 AI-powered intelligence modules working together</p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>
          {FEATURES.map(f => (
            <div key={f.title} className="glass-card" style={{ padding: "24px" }}>
              <div style={{ fontSize: "32px", marginBottom: "12px" }}>{f.icon}</div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "8px" }}>{f.title}</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats bar */}
      <section className="container" style={{ marginTop: "72px" }}>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "24px", padding: "40px", borderRadius: "20px",
          background: "linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.05) 100%)",
          border: "1px solid rgba(99,102,241,0.2)",
        }}>
          {STATS.map(s => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <div style={{ fontSize: "36px", fontWeight: 800, background: "var(--gradient-hero)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>{s.value}</div>
              <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

const FEATURES = [
  { icon: "🏪", title: "Business Recommendation", desc: "Get AI-powered suggestions on which cuisine & business type to launch in your target area." },
  { icon: "💰", title: "Pricing Intelligence", desc: "Optimal pricing using price elasticity and competitor benchmarking." },
  { icon: "📋", title: "Menu Generator", desc: "Curated dish recommendations ranked by demand score and sentiment." },
  { icon: "📊", title: "Demand-Gap Analysis", desc: "Identify high demand, low supply opportunities before competitors do." },
  { icon: "📈", title: "Trend Detection", desc: "Rising and declining cuisine trends with demand growth rates." },
  { icon: "💬", title: "Sentiment Engine", desc: "Aspect-level analysis: taste, service, and price sentiment from reviews." },
  { icon: "⏰", title: "Peak Hour Analyzer", desc: "Busiest hour identification for staffing and offer optimization." },
  { icon: "🤝", title: "Combo Engine", desc: "Association-based dish combinations and bundle pricing suggestions." },
  { icon: "🔮", title: "Scenario Simulator", desc: "Simulate launching a new business and predict the market impact." },
  { icon: "🗺️", title: "Area Heatmap", desc: "Geographic demand and competition visualization across city areas." },
  { icon: "🥊", title: "Competitor Analysis", desc: "Compare your restaurant against area competitors on all key metrics." },
  { icon: "🎯", title: "Improvement Engine", desc: "Prioritized, actionable improvement recommendations for your restaurant." },
];

const STATS = [
  { value: "1,200+", label: "Market Records" },
  { value: "14", label: "Intelligence Modules" },
  { value: "7", label: "Indian Cities" },
  { value: "15", label: "Cuisine Types" },
];
