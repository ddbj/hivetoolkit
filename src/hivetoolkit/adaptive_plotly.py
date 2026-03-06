"""
adaptive_plotly.py

Notebook-first Plotly renderer that:
- Detects background color in the frontend (VS Code / JupyterLab / classic Notebook).
- Adapts Plotly layout colors (font/axes/grid) for readability.
- Avoids re-injecting plotly.js by injecting it only once per notebook session.

Design notes:
- This module targets notebook display, not HTML export stability.
- It does NOT try to send theme info back to Python; it keeps the logic in JS.
"""

from __future__ import annotations

import json
import uuid
from typing import Optional, Dict, Any
import importlib.resources

from IPython.display import HTML, Javascript, display
import plotly.graph_objects as go
import plotly.io as pio

def show_adaptive(fig: go.Figure, *, config: Optional[Dict[str, Any]] = None, div_id: Optional[str] = None) -> None:
    """
    Render a Plotly figure with adaptive colors for notebook backgrounds.

    Usage:
        show_adaptive(fig)

    Behavior:
    - Reads background color from CSS variables (VS Code / JupyterLab fallback) or body background.
    - Chooses dark/light foreground + grid colors based on luminance.
    - Renders the figure into a dedicated div using Plotly.newPlot().
    """
    if div_id is None:
        div_id = "plot_" + uuid.uuid4().hex

    #region extract plotly.js code
    # Ensure plotly.js is available. If the frontend isolates outputs, this injection may still be required before each render.
    # Get a Plotly HTML stub that includes plotly.js inline.
    # We will extract the largest <script> block, which is effectively the plotly.js bundle.
    stub_html = pio.to_html(
        {"data": [], "layout": {}},
        include_plotlyjs="inline",
        full_html=False,
    )
    plotly_js = _extract_largest_script_block(stub_html)
    #endregion extract plotly.js code

    fig_json = fig.to_json()
    config_json = json.dumps(config)

    # Gets the JS code from adaptive_plotly.js
    js_code = importlib.resources.files("hivetoolkit").joinpath("adaptive_plotly.js").read_text(encoding="utf-8")
    
    display(HTML(f"""
<div id="{div_id}"></div>
<script>
/* ---- plotly.js (inline, injected once) ---- */
{plotly_js}
</script>
<script>
(function(){{
  // --- receives data from Python ---
  const fig = JSON.parse({json.dumps(fig_json)});
  fig.layout = fig.layout || {{}};
  const config = ((typeof {config_json} == 'string') ? JSON.parse({config_json}) : {config_json}) || {{}};
""" +
    js_code + f"""
  // --- ERROR message ---
  if (typeof Plotly === "undefined") {{
    const pre = document.createElement("pre");
    pre.textContent = "ERROR: Plotly is undefined in this output context.";
    pre.style.padding = "8px";
    pre.style.border = "1px solid #c003";
    pre.style.borderRadius = "6px";
    document.getElementById("{div_id}").appendChild(pre);
    return;
  }}
  // --- Draws figure by calling Plotly.newPlot ---
  Plotly.newPlot("{div_id}", fig.data, fig.layout, config || fig.config || {{}});
}})();
</script>
"""))


def _extract_largest_script_block(html: str) -> str:
    """
    Extract all <script>...</script> blocks and return the largest one.
    For Plotly's inline HTML, the plotly.js bundle is typically the largest script.
    """
    import re

    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.DOTALL | re.IGNORECASE)
    if not scripts:
        raise RuntimeError("No <script> blocks found in Plotly HTML.")
    return max(scripts, key=len)
