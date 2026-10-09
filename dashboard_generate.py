"""
dashboard_generate.py

Generates a self-contained HTML dashboard from all IFC files in sample_data/,
using the exact same compliance logic your MCP server exposes as
check_grz_compliance. Run this after generate_test_ifc.py has produced
your IFC files.

Usage: python3 dashboard_generate.py
Then open dashboard.html in your browser.
"""

import glob
import os
from ifc_tools import calculate_coverage_ratio, read_plot_metadata
from regulation_client import get_regulatory_grz, is_fabricated_report

OUTPUT_PATH = "dashboard.html"


def score_plot(ifc_path):
    meta = read_plot_metadata(ifc_path)
    computed = calculate_coverage_ratio(ifc_path)
    plot_id = meta["plot_name"].split(" - ")[0].replace("Plot ", "").replace("Zone", "").strip()

    try:
        regulation = get_regulatory_grz(plot_id)
    except Exception as e:
        regulation = {"extracted_grz": None, "analysis_text": f"Error calling regulation API: {e}"}

    extracted = regulation["extracted_grz"]
    fabricated = is_fabricated_report(regulation.get("analysis_text", ""))

    if extracted is None:
        outcome = "N/A"
    elif computed["computed_coverage_ratio"] <= extracted + 0.02:
        outcome = "within"
    else:
        outcome = "exceeds"

    return {
        "file": os.path.basename(ifc_path),
        "plot_name": meta["plot_name"],
        "gold_grz": meta["gold_grz"],
        "computed_grz": computed["computed_coverage_ratio"],
        "regulatory_grz": extracted,
        "outcome": outcome,
        "fabricated": fabricated,
        "analysis_text": regulation.get("analysis_text", ""),
    }


def render_card(r):
    colors = {"within": "#2BD9B0", "exceeds": "#E2574C", "N/A": "#7A8794"}
    labels = {"within": "Within regulatory limit", "exceeds": "Exceeds regulatory limit", "N/A": "No value asserted"}
    color = colors[r["outcome"]]
    label = labels[r["outcome"]]

    computed_pct = min(r["computed_grz"] * 100, 100) if r["computed_grz"] is not None else 0
    reg_pct = min(r["regulatory_grz"] * 100, 100) if r["regulatory_grz"] is not None else 0

    fab_badge = '<span class="fab-badge">FABRICATED REPORT DETECTED</span>' if r["fabricated"] else ""

    return f"""
    <div class="card" style="border-color:{color}">
      <div class="card-head">
        <h3>{r['plot_name']}</h3>
        <span class="badge" style="background:{color}22;color:{color};border-color:{color}">{label}</span>
      </div>
      {fab_badge}
      <div class="bars">
        <div class="bar-row">
          <span class="bar-label">As-built (computed)</span>
          <div class="bar-track"><div class="bar-fill" style="width:{computed_pct}%;background:#3399cc"></div></div>
          <span class="bar-value">{r['computed_grz']}</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">System's stated limit</span>
          <div class="bar-track"><div class="bar-fill" style="width:{reg_pct}%;background:{color}"></div></div>
          <span class="bar-value">{r['regulatory_grz'] if r['regulatory_grz'] is not None else '—'}</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">Verified gold GRZ</span>
          <div class="bar-track"><div class="bar-fill" style="width:{r['gold_grz']*100}%;background:#F2A93C"></div></div>
          <span class="bar-value">{r['gold_grz']}</span>
        </div>
      </div>
      <details>
        <summary>System's full analysis text</summary>
        <pre>{r['analysis_text']}</pre>
      </details>
    </div>
    """


def main():
    ifc_files = sorted(glob.glob("sample_data/*.ifc"))
    if not ifc_files:
        print("No IFC files found in sample_data/. Run generate_test_ifc.py first.")
        return

    results = []
    for path in ifc_files:
        print(f"Scoring {path}...")
        results.append(score_plot(path))

    cards_html = "\n".join(render_card(r) for r in results)

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Stuttgart Regulatory AI - Compliance Dashboard</title>
<style>
  body {{ background:#0E1B2B; color:#FFFFFF; font-family:sans-serif; margin:0; padding:40px; }}
  .kicker {{ color:#F2A93C; font-size:11px; font-weight:700; letter-spacing:1.5px; }}
  h1 {{ font-size:26px; margin:8px 0 4px; }}
  .sub {{ color:#93A0AE; font-size:14px; margin-bottom:32px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(360px,1fr)); gap:20px; }}
  .card {{ background:#142639; border:1.5px solid #3A4B5E; border-radius:12px; padding:20px; }}
  .card-head {{ display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:8px; }}
  .card-head h3 {{ font-size:15px; margin:0; }}
  .badge {{ font-size:11px; font-weight:700; padding:4px 10px; border-radius:12px; border:1px solid; white-space:nowrap; }}
  .fab-badge {{ display:inline-block; background:#E2574C22; color:#E2574C; border:1px solid #E2574C; font-size:10px; font-weight:700; padding:3px 8px; border-radius:8px; margin-bottom:12px; }}
  .bars {{ margin:12px 0; }}
  .bar-row {{ display:grid; grid-template-columns:130px 1fr 50px; align-items:center; gap:8px; margin-bottom:8px; font-size:11px; }}
  .bar-label {{ color:#93A0AE; }}
  .bar-track {{ height:8px; background:#0E1B2B; border-radius:4px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:4px; }}
  .bar-value {{ text-align:right; font-weight:700; }}
  details {{ margin-top:12px; font-size:12px; }}
  summary {{ cursor:pointer; color:#93A0AE; }}
  pre {{ white-space:pre-wrap; color:#C7CED6; background:#0E1B2B; padding:12px; border-radius:8px; max-height:240px; overflow-y:auto; font-size:11px; }}
</style></head>
<body>
  <div class="kicker">STUTTGART REGULATORY AI</div>
  <h1>Compliance Dashboard</h1>
  <div class="sub">{len(results)} plots scored via the ifc-compliance MCP server's underlying logic</div>
  <div class="grid">
    {cards_html}
  </div>
</body></html>"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nDone. Open {OUTPUT_PATH} in your browser.")


if __name__ == "__main__":
    main()