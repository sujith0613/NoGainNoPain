import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TasteIntel — Food Market Intelligence & Decision Engine",
  description: "AI-powered food market intelligence for new and existing business owners",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="container">
            <div className="nav-inner">
              <a href="/" style={{ textDecoration: "none" }}>
                <span className="nav-logo">🍽️ TasteIntel</span>
              </a>
              <div className="nav-links">
                <a href="/start-business"><button className="btn-secondary">Start a Business</button></a>
                <a href="/improve-business"><button className="btn-secondary">Improve My Business</button></a>
              </div>
            </div>
          </div>
        </nav>
        <main className="page-wrapper">
          {children}
        </main>
      </body>
    </html>
  );
}
