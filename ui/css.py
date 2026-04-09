"""
Stitch Design System — Complete CSS for ScholAR Pulse.
Pixel-perfect replication of the Cinematic Intelligence Framework.
"""
import streamlit as st


def inject_css():
    """Inject the full Stitch CSS into the Streamlit app."""
    st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=Manrope:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
  --bg: #111319;
  --surface: #111319;
  --surface-container: #1e1f26;
  --surface-container-low: #191b22;
  --surface-container-high: #282a30;
  --surface-container-highest: #33343b;
  --surface-bright: #373940;
  --cyan: #00f2ff;
  --primary: #00f2ff;
  --primary-dim: #00dbe7;
  --purple: #8a2be2;
  --secondary: #dcb8ff;
  --red: #ff3131;
  --error: #ffb4ab;
  --orange: #f59e0b;
  --blue: #3b82f6;
  --green: #10b981;
  --on-surface: #e2e2eb;
  --on-surface-variant: #b9cacb;
  --outline: #849495;
  --outline-variant: #3a494b;
  --glass: rgba(25, 27, 34, 0.7);
  --glass-light: rgba(30, 31, 38, 0.5);
  --border: rgba(0, 242, 255, 0.2);
  --border-ghost: rgba(0, 242, 255, 0.08);
  --glow-cyan: 0 0 10px rgba(0, 242, 255, 0.05);
  --glow-red: 0 0 10px rgba(255, 49, 49, 0.05);
}

/* ═══════════════════════ BASE ═══════════════════════ */
html, body, [class*="css"] {
  font-family: 'Inter', 'Outfit', sans-serif !important;
  color: var(--on-surface);
}
.stApp {
  background-color: var(--bg) !important;
  background-image: radial-gradient(circle, rgba(0,242,255,0.04) 1px, transparent 1px);
  background-size: 32px 32px;
}
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; color: var(--on-surface); }
p, span, div { color: var(--on-surface); }

/* ═══════════════════════ HEADER ═══════════════════════ */
header[data-testid="stHeader"] { background: transparent !important; }

/* ═══════════════════════ SIDEBAR ═══════════════════════ */
div[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #06080d 0%, #0d1117 100%) !important;
  border-right: 1px solid rgba(0,242,255,0.06) !important;
}
div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: #94a3b8;
}

/* ═══════════════════════ TABS ═══════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  gap: 0;
  background: var(--surface-container);
  border-radius: 10px;
  padding: 4px;
  border: 0.5px solid var(--border-ghost);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  color: #64748b;
  font-family: 'Manrope', sans-serif;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
  background: rgba(0,242,255,0.08) !important;
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
}

/* ═══════════════════════ BUTTONS ═══════════════════════ */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #00f2ff 0%, #00dbe7 100%) !important;
  color: #002022 !important;
  font-family: 'Manrope', sans-serif !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 8px !important;
  box-shadow: 0 0 20px rgba(0,242,255,0.2);
  transition: all 0.3s ease;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 0 30px rgba(0,242,255,0.3);
  transform: translateY(-1px);
}
.stButton > button[kind="secondary"], .stButton > button:not([kind]) {
  background: transparent !important;
  border: 0.5px solid rgba(0,242,255,0.2) !important;
  color: var(--cyan) !important;
  font-family: 'Manrope', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
}
.stButton > button[kind="secondary"]:hover, .stButton > button:not([kind]):hover {
  background: rgba(0,242,255,0.05) !important;
  border-color: rgba(0,242,255,0.4) !important;
}

/* ═══════════════════════ INPUTS ═══════════════════════ */
.stTextInput input, .stSelectbox select, div[data-baseweb="select"] {
  background: var(--surface-container) !important;
  border: 0.5px solid var(--border-ghost) !important;
  color: var(--on-surface) !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 1px var(--cyan), 0 0 15px rgba(0,242,255,0.1) !important;
}

/* ═══════════════════════ SLIDER ═══════════════════════ */
.stSlider [data-baseweb="slider"] [role="slider"] {
  background: var(--cyan) !important;
  box-shadow: 0 0 10px rgba(0,242,255,0.4);
}

/* ═══════════════════════ EXPANDER ═══════════════════════ */
.streamlit-expanderHeader {
  background: var(--surface-container) !important;
  border-radius: 8px !important;
  border: 0.5px solid var(--border-ghost) !important;
  color: var(--on-surface) !important;
}

/* ═══════════════════════ DATAFRAME ═══════════════════════ */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ═══════════════════════ DOWNLOAD BUTTON ═══════════════════════ */
.stDownloadButton > button {
  background: linear-gradient(135deg, #00f2ff 0%, #00dbe7 100%) !important;
  color: #002022 !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 8px !important;
}

/* ═══════════════════════ ANIMATIONS ═══════════════════════ */
@keyframes pulse-cyan {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,242,255,0.4); }
  50% { box-shadow: 0 0 0 8px rgba(0,242,255,0); }
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes glow-ring {
  0%, 100% { filter: drop-shadow(0 0 6px rgba(0,242,255,0.3)); }
  50% { filter: drop-shadow(0 0 12px rgba(0,242,255,0.6)); }
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.animate-fade-in { animation: fadeSlideIn 0.4s ease-out both; }
.pulse-glow { animation: pulse-cyan 2s infinite; }

/* ═══════════════════════ GLASS PANELS ═══════════════════════ */
.glass-panel {
  backdrop-filter: blur(20px);
  background: var(--glass);
  border: 0.5px solid var(--border);
  box-shadow: var(--glow-cyan);
  border-radius: 12px;
}
.glass-panel-error {
  backdrop-filter: blur(20px);
  background: var(--glass);
  border: 0.5px solid rgba(255,49,49,0.2);
  box-shadow: var(--glow-red);
  border-radius: 12px;
}

/* ═══════════════════════ METRIC CARDS ═══════════════════════ */
.metric-card-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 32px; }
@media (max-width: 900px) { .metric-card-grid { grid-template-columns: repeat(2, 1fr); } }

/* ═══════════════════════ AGENT BAR ═══════════════════════ */
.agent-bar {
  display: flex; justify-content: space-around; align-items: center;
  background: var(--glass); border: 0.5px solid var(--border);
  border-radius: 12px; padding: 16px; margin-bottom: 20px;
  backdrop-filter: blur(20px);
}
.agent-node {
  display: flex; flex-direction: column; align-items: center;
  gap: 6px; opacity: 0.35; transition: all 0.4s ease;
}
.agent-node.active { opacity: 1; }
.agent-node.done { opacity: 0.75; }
.agent-icon { font-size: 28px; transition: all 0.3s; }
.agent-node.active .agent-icon { animation: pulse-cyan 1.5s infinite; }
.agent-label {
  font-family: 'Manrope', sans-serif; font-size: 10px;
  letter-spacing: 0.1em; text-transform: uppercase;
}

/* ═══════════════════════ THINKING CARDS ═══════════════════════ */
.thinking-event {
  display: flex; gap: 16px; margin-bottom: 16px; align-items: flex-start;
  animation: fadeSlideIn 0.4s ease-out both;
}
.thinking-timestamp {
  font-size: 10px; font-family: 'Courier New', monospace;
  color: #64748b; padding-top: 4px; min-width: 50px;
}
.thinking-card {
  flex: 1; background: var(--glass-light); border-radius: 8px; padding: 14px;
  position: relative; overflow: hidden;
  border: 1px solid rgba(132,148,149,0.1);
}
.thinking-card-icon-bg {
  position: absolute; top: 0; right: 0;
  opacity: 0.04; transform: translate(30%, -30%); font-size: 64px;
}

/* ═══════════════════════ PAPER CARDS ═══════════════════════ */
.paper-card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 20px; }

/* ═══════════════════════ NAVIGATION PILLS ═══════════════════════ */
.nav-section { padding: 4px 0; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 20px; color: #64748b; cursor: pointer;
  transition: all 0.3s; border-left: 2px solid transparent;
  font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500;
  text-decoration: none;
}
.nav-item:hover { color: #00dbe7; background: rgba(255,255,255,0.03); }
.nav-item.active {
  color: #00f2ff; border-left-color: #00f2ff;
  background: rgba(0,242,255,0.05);
}

/* ═══════════════════════ HIDE STREAMLIT DEFAULTS ═══════════════════════ */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
''', unsafe_allow_html=True)
