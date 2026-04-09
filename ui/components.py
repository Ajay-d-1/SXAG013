"""
Reusable UI helper functions for the Stitch design system.
"""
import streamlit as st
import streamlit.components.v1 as components
import html as _html


def esc(text):
    """HTML-escape dynamic text to prevent rendering breakage."""
    if text is None:
        return ""
    return _html.escape(str(text))


def safe_html_render(html_content, height=None):
    """Safely render HTML content using components.v1.html for reliability."""
    if height:
        components.html(html_content, height=height)
    else:
        st.markdown(html_content, unsafe_allow_html=True)


def safe_score(val, default=5):
    """Ensure a score is a numeric value."""
    if isinstance(val, str):
        try:
            return float(val.split("/")[0])
        except (ValueError, IndexError):
            return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def render_confidence_ring(confidence_pct, size=180):
    """Render an SVG radial confidence meter matching Stitch design."""
    r = size // 2 - 12
    circumference = 2 * 3.14159 * r
    offset = circumference * (1 - confidence_pct / 100)
    status = "OPTIMAL" if confidence_pct >= 80 else "GOOD" if confidence_pct >= 60 else "LOW"
    status_color = "#00f2ff" if confidence_pct >= 80 else "#f59e0b" if confidence_pct >= 60 else "#ff3131"
    cx = size // 2
    cy = size // 2

    return f'''
    <div style="display:flex;flex-direction:column;align-items:center;padding:24px 0;">
      <div style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:20px;">System Confidence</div>
      <div style="position:relative;width:{size}px;height:{size}px;">
        <svg width="{size}" height="{size}" style="transform:rotate(-90deg);">
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="#33343b" stroke-width="4"/>
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="{status_color}" stroke-width="7"
            stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
            style="filter:drop-shadow(0 0 8px {status_color});transition:stroke-dashoffset 1.5s ease;"/>
        </svg>
        <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <span style="font-size:36px;font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;">{confidence_pct:.0f}%</span>
          <span style="font-size:10px;font-family:Manrope,sans-serif;color:{status_color};text-transform:uppercase;letter-spacing:0.15em;">{status}</span>
        </div>
      </div>
    </div>
    '''


def render_glass_card(content_html, border_color="rgba(0,242,255,0.2)", extra_style=""):
    """Render content inside a Stitch glass panel."""
    return f'''
    <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid {border_color};
      box-shadow:0 0 10px rgba(0,242,255,0.05);border-radius:12px;padding:24px;{extra_style}">
      {content_html}
    </div>
    '''


def output_glass_card(content_html, border_color="rgba(0,242,255,0.2)", extra_style="", height=None):
    """Output a glass card directly to streamlit using components.v1.html."""
    html = f'''
    <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid {border_color};
      box-shadow:0 0 10px rgba(0,242,255,0.05);border-radius:12px;padding:24px;{extra_style}">
      {content_html}
    </div>
    '''
    if height:
        components.html(html, height=height)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render_metric_card(label, value, subtitle, icon, accent_color="#00f2ff", bar_width="75%"):
    """Render a single metric card matching Stitch analytics dashboard."""
    is_error = accent_color in ["#ff3131", "#ffb4ab"]
    border = f"rgba(255,49,49,0.2)" if is_error else f"rgba(0,242,255,0.2)"
    glow = f"0 0 10px rgba(255,49,49,0.05)" if is_error else f"0 0 10px rgba(0,242,255,0.05)"
    return f'''
    <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid {border};
      box-shadow:{glow};border-radius:12px;padding:24px;position:relative;overflow:hidden;
      transition:all 0.3s ease;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
        <span style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.15em;">{label}</span>
        <span style="font-size:20px;">{icon}</span>
      </div>
      <div style="display:flex;flex-direction:column;">
        <span style="font-size:28px;font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;margin-bottom:4px;">{value}</span>
        <span style="font-size:11px;font-family:Manrope,sans-serif;color:{accent_color};display:flex;align-items:center;gap:4px;">{subtitle}</span>
      </div>
      <div style="position:absolute;bottom:0;left:0;height:3px;
        background:linear-gradient(90deg,{accent_color},transparent);width:{bar_width};
        transition:width 0.7s ease;"></div>
    </div>
    '''


def render_metrics_row(results):
    """Render the full 4-card metrics row from analysis results."""
    if not results:
        return

    papers_count = results.get("papers_count", len(st.session_state.get("papers", [])))
    contradictions_count = results.get("contradictions_count", len(st.session_state.get("contradictions", [])))
    confidence = results.get("confidence", 0)
    avg_cred = results.get("avg_credibility", 0)

    if isinstance(avg_cred, str):
        avg_cred = safe_score(avg_cred)

    cred_label = "A+" if avg_cred >= 8 else "A" if avg_cred >= 7 else "B+" if avg_cred >= 6 else "B" if avg_cred >= 5 else "C"

    cards = [
        render_metric_card("Dataset Size", f"{papers_count:,}", "Analyzed", "&#128196;", "#00f2ff", "75%"),
        render_metric_card("Anomalies", str(contradictions_count),
            f"Conflict{'s' if contradictions_count != 1 else ''} Detected" if contradictions_count > 0 else "Clean",
            "&#10071;", "#ff3131" if contradictions_count > 0 else "#10b981", f"{min(contradictions_count * 15, 50)}%"),
        render_metric_card("AI Consensus", f"{confidence:.0%}", "High Precision" if confidence >= 0.8 else "Building", "&#128300;", "#dcb8ff", f"{confidence * 100:.0f}%"),
        render_metric_card("Source Trust", cred_label, f"{avg_cred:.1f}/10 Average", "&#9881;", "#00dbe7", f"{avg_cred * 10:.0f}%"),
    ]

    html_content = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:28px;">'
    html_content += "".join(cards)
    html_content += '</div>'
    # Use components.v1.html for more reliable rendering
    components.html(html_content, height=160)


def render_insight_card(icon, title, text, accent_color="#00f2ff"):
    """Render an insight card (Key Insight, Field Momentum, Red Flags)."""
    return f'''
    <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.5);border-radius:12px;padding:24px;
      border:1px solid transparent;transition:all 0.3s ease;min-height:150px;">
      <div style="font-size:24px;margin-bottom:14px;">{icon}</div>
      <div style="font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;margin-bottom:8px;font-size:15px;">{title}</div>
      <div style="font-size:12px;color:#94a3b8;line-height:1.6;">{text}</div>
    </div>
    '''


def output_insight_card(icon, title, text, accent_color="#00f2ff", height=160):
    """Output an insight card directly using components.v1.html."""
    html = render_insight_card(icon, title, text, accent_color)
    components.html(html, height=height)


def render_badge(text, color="#00f2ff", bg_opacity=0.15):
    """Render a small inline badge/chip."""
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return f'<span style="font-size:10px;font-family:Manrope,sans-serif;font-weight:600;color:{color};background:rgba({r},{g},{b},{bg_opacity});padding:3px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:0.05em;">{text}</span>'


def render_section_header(title, subtitle="", ref_id=""):
    """Render a section header with optional reference ID."""
    ref_html = f'<span style="position:absolute;top:16px;right:24px;font-size:10px;font-family:Courier New,monospace;color:#3a494b;">{ref_id}</span>' if ref_id else ""
    sub_html = f'<div style="font-size:12px;color:#64748b;margin-top:4px;font-family:Manrope,sans-serif;">{subtitle}</div>' if subtitle else ""
    return f'''
    <div style="position:relative;margin-bottom:20px;">
      {ref_html}
      <h2 style="font-family:Space Grotesk,sans-serif;font-size:22px;font-weight:700;color:#e2e2eb;display:flex;align-items:center;gap:10px;margin:0;">
        <span style="width:8px;height:8px;border-radius:50%;background:#00f2ff;box-shadow:0 0 8px #00f2ff;display:inline-block;"></span>
        {title}
      </h2>
      {sub_html}
    </div>
    '''


def render_page_header(title, subtitle="", show_badge=True):
    """Render a large page title banner."""
    badge = '<div style="display:inline-block;font-size:10px;font-family:Manrope,sans-serif;color:#00f2ff;background:rgba(0,242,255,0.08);border:0.5px solid rgba(0,242,255,0.2);padding:4px 14px;border-radius:20px;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">● AUTONOMOUS RESEARCH ENGINE V4.0</div>' if show_badge else ""
    sub = f'<div style="font-size:14px;color:#94a3b8;margin-top:6px;font-family:Inter,sans-serif;">{subtitle}</div>' if subtitle else ""
    return f'''
    <div style="text-align:center;padding:20px 0 16px;">
      {badge}
      <h1 style="font-family:Space Grotesk,sans-serif;font-size:32px;font-weight:700;color:#e2e2eb;margin:8px 0 0;">{title}</h1>
      {sub}
    </div>
    '''


def output_page_header(title, subtitle="", show_badge=True):
    """Output page header directly."""
    html = render_page_header(title, subtitle, show_badge)
    st.markdown(html, unsafe_allow_html=True)
