import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: #f8f9fb;
    color: #1a1d23;
    min-height: 100vh;
  }

  .app { max-width: 1280px; margin: 0 auto; padding: 32px 24px; }

  .header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid #e5e8ef;
  }

  .header-left h1 {
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #0f1117;
  }

  .header-left p {
    font-size: 13px;
    color: #8a8fa8;
    margin-top: 3px;
    font-weight: 400;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .live-dot {
    width: 7px;
    height: 7px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  .updated-text {
    font-size: 12px;
    color: #adb2c4;
    font-family: 'DM Mono', monospace;
  }

  .risk-pill {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    padding: 5px 12px;
    border-radius: 100px;
    text-transform: uppercase;
  }

  .risk-low { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
  .risk-medium { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
  .risk-high { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 20px;
  }

  .metric-card {
    background: #fff;
    border: 1px solid #e8ebf2;
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }

  .metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
  }

  .metric-ok::before { background: #22c55e; }
  .metric-warning::before { background: #f59e0b; }
  .metric-critical::before { background: #ef4444; }

  .metric-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #9ca3b0;
    margin-bottom: 10px;
  }

  .metric-value {
    font-size: 32px;
    font-weight: 300;
    letter-spacing: -1px;
    line-height: 1;
    font-family: 'DM Mono', monospace;
  }

  .metric-ok .metric-value { color: #15803d; }
  .metric-warning .metric-value { color: #b45309; }
  .metric-critical .metric-value { color: #b91c1c; }

  .metric-unit {
    font-size: 13px;
    font-weight: 400;
    color: #c4c8d6;
    margin-left: 4px;
    font-family: 'DM Sans', sans-serif;
  }

  .middle-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 16px;
    margin-bottom: 20px;
  }

  .card {
    background: #fff;
    border: 1px solid #e8ebf2;
    border-radius: 12px;
    padding: 20px;
  }

  .card-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #9ca3b0;
    margin-bottom: 16px;
  }

  .alert-item {
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 12px;
    line-height: 1.5;
    margin-bottom: 8px;
    border-left: 3px solid;
  }

  .alert-ok { background: #f0fdf4; border-color: #22c55e; color: #166534; }
  .alert-warning { background: #fffbeb; border-color: #f59e0b; color: #92400e; }
  .alert-critical { background: #fef2f2; border-color: #ef4444; color: #991b1b; }

  .alert-level {
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 2px;
  }

  .bottom-grid {
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap: 16px;
  }

  .summary-text {
    font-size: 14px;
    line-height: 1.75;
    color: #374151;
    font-weight: 400;
  }

  .prediction-score {
    font-size: 52px;
    font-weight: 300;
    font-family: 'DM Mono', monospace;
    letter-spacing: -2px;
    line-height: 1;
    margin-bottom: 4px;
  }

  .prediction-label {
    font-size: 12px;
    color: #9ca3b0;
    margin-bottom: 20px;
  }

  .factor-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f8;
    font-size: 12px;
  }

  .factor-row:last-child { border-bottom: none; }

  .factor-name { color: #6b7280; font-family: 'DM Mono', monospace; font-size: 11px; }
  .factor-val { color: #374151; font-weight: 500; }

  .loading {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Sans', sans-serif;
    color: #9ca3b0;
    font-size: 14px;
    background: #f8f9fb;
  }

  .section-divider {
    width: 100%;
    height: 1px;
    background: #e8ebf2;
    margin: 4px 0 16px;
  }
`;

function getMetricClass(value, warning, critical) {
  if (value >= critical) return "metric-card metric-critical";
  if (value >= warning) return "metric-card metric-warning";
  return "metric-card metric-ok";
}

function getRiskClass(level) {
  if (level === "high") return "risk-pill risk-high";
  if (level === "medium") return "risk-pill risk-medium";
  return "risk-pill risk-low";
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#fff', border: '1px solid #e8ebf2', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
        <p style={{ color: '#9ca3b0', marginBottom: 6, fontFamily: 'DM Mono', fontSize: 11 }}>{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color, fontWeight: 500 }}>{p.name}: {p.value} min</p>
        ))}
      </div>
    );
  }
  return null;
};

export default function App() {
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = async () => {
    try {
      const res = await axios.get(`${API}/summary`);
      const data = res.data;
      setSummary(data);
      setLastUpdated(new Date().toLocaleTimeString());
      setHistory(prev => {
        const newPoint = {
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          ED: data.metrics.ed_avg_wait_minutes,
          ICU: data.metrics.icu_avg_wait_minutes,
          Lab: data.metrics.lab_avg_wait_minutes,
        };
        return [...prev, newPoint].slice(-20);
      });
    } catch (err) {
      console.error("Failed to fetch", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading HospitalFlow AI...</div>;

  const m = summary?.metrics;
  const p = summary?.prediction;
  const alerts = summary?.alerts || [];

  return (
    <>
      <style>{styles}</style>
      <div className="app">

        <div className="header">
          <div className="header-left">
            <h1>HospitalFlow AI</h1>
            <p>Real-time Emergency Department Operations Intelligence</p>
          </div>
          <div className="header-right">
            <div className="live-dot" />
            <span className="updated-text">{lastUpdated || '—'}</span>
            {p && <span className={getRiskClass(p.risk_level)}>{p.risk_level} risk</span>}
          </div>
        </div>

        <div className="metrics-grid">
          {[
            { label: "ED Avg Wait", value: m?.ed_avg_wait_minutes, warning: 60, critical: 90 },
            { label: "ICU Avg Wait", value: m?.icu_avg_wait_minutes, warning: 50, critical: 80 },
            { label: "Lab Turnaround", value: m?.lab_avg_wait_minutes, warning: 60, critical: 90 },
            { label: "Discharge Wait", value: m?.discharge_avg_wait_minutes, warning: 50, critical: 75 },
          ].map((item, i) => (
            <div key={i} className={getMetricClass(item.value, item.warning, item.critical)}>
              <div className="metric-label">{item.label}</div>
              <div className="metric-value">
                {item.value ?? '—'}
                <span className="metric-unit">min</span>
              </div>
            </div>
          ))}
        </div>

        <div className="middle-grid">
          <div className="card">
            <div className="card-title">Wait Time Trends</div>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={history} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f1f5" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#c4c8d6', fontFamily: 'DM Mono' }} />
                <YAxis tick={{ fontSize: 10, fill: '#c4c8d6', fontFamily: 'DM Mono' }} />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine y={90} stroke="#fecaca" strokeDasharray="4 4" />
                <Line type="monotone" dataKey="ED" stroke="#ef4444" strokeWidth={1.5} dot={false} name="ED" />
                <Line type="monotone" dataKey="ICU" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="ICU" />
                <Line type="monotone" dataKey="Lab" stroke="#3b82f6" strokeWidth={1.5} dot={false} name="Lab" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="card-title">Active Alerts</div>
            {alerts.map((a, i) => (
              <div key={i} className={`alert-item alert-${a.level}`}>
                <span className="alert-level">{a.level}</span>
                {a.message}
              </div>
            ))}
          </div>
        </div>

        <div className="bottom-grid">
          <div className="card">
            <div className="card-title">AI Incident Summary</div>
            <div className="section-divider" />
            <p className="summary-text">{summary?.summary || '—'}</p>
          </div>

          <div className="card">
            <div className="card-title">ML Risk Prediction</div>
            <div className="section-divider" />
            <div className={`prediction-score ${p?.risk_level === 'high' ? 'risk-high' : p?.risk_level === 'medium' ? 'risk-medium' : 'risk-low'}`} style={{ color: p?.risk_level === 'high' ? '#b91c1c' : p?.risk_level === 'medium' ? '#b45309' : '#15803d' }}>
              {Math.round((p?.risk_score || 0) * 100)}
              <span style={{ fontSize: 20, fontWeight: 400, marginLeft: 2 }}>%</span>
            </div>
            <div className="prediction-label">{p?.prediction}</div>
            {p?.top_factors?.map((f, i) => (
              <div key={i} className="factor-row">
                <span className="factor-name">{f.factor}</span>
                <span className="factor-val">{f.current_value}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </>
  );
}