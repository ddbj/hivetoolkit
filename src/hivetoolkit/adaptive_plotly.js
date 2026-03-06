
  // --- Background color detection (VS Code / JupyterLab / classic Notebook) ---
  const styles = getComputedStyle(document.documentElement);
  const bg = (
        styles.getPropertyValue('--vscode-editor-background').trim()
     || styles.getPropertyValue('--jp-layout-color0').trim()
     || getComputedStyle(document.body).backgroundColor
     || ""
  ).trim();

  function cssToRgb(css){
    css = (css || "").trim();

    // #rgb
    if (/^#([0-9a-f]{3})$/i.test(css)) {
      const h = css.substring(1);
      return {
        r: parseInt(h[0] + h[0], 16),
        g: parseInt(h[1] + h[1], 16),
        b: parseInt(h[2] + h[2], 16),
      };
    }

    // #rrggbb
    if (/^#([0-9a-f]{6})$/i.test(css)) {
      const h = css.substring(1);
      return {
        r: parseInt(h.slice(0, 2), 16),
        g: parseInt(h.slice(2, 4), 16),
        b: parseInt(h.slice(4, 6), 16),
      };
    }

    // rgb(r,g,b)
    let m = css.match(/^rgb\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\)$/i);
    if (m) {
      return { r: +m[1], g: +m[2], b: +m[3] };
    }

    // rgba(r,g,b,a) -> ignore alpha
    m = css.match(/^rgba\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*([0-9.]+)\\s*\\)$/i);
    if (m) {
      return { r: +m[1], g: +m[2], b: +m[3] };
    }

    return null;
  }

  function isDark(rgb){
    // Simple relative luminance thresholding
    const lum = 0.2126 * rgb.r + 0.7152 * rgb.g + 0.0722 * rgb.b;
    return lum < 128;
  }

  const rgb = cssToRgb(bg);
  const dark = rgb ? isDark(rgb) : false;

  const fg = dark ? "#ffffff" : "#000000";
  const grid = dark ? "rgba(255,255,255,0.18)" : "rgba(0,0,0,0.12)";
  const annbg = dark ? "rgba(0,0,0,0.6)" : "rgba(255,255,255,0.6)";

  function mapColorForHeatmapColorscale(color, dark) {
    //console.error(`mapColorForHeatmapColorscale called color=${color} dark=${dark}`); // DEBUG
    if (!dark) return color;
    if (!color) return color;
    const c = color.toLowerCase();
    if (c === "white" || c === "#ffffff") return "black";
    if (c === "cyan" || c === "#00ffff") return "blue";
    return color;
  }

  function rewriteColorscale(fig, trace, dark) {
    //console.error(`rewriteColorscale trace type: ${typeof trace}; class ${trace.constructor}; has colorscale ${"colorscale" in trace}`); // DEBUG
    // Heatmap colorscale
    if (trace.colorscale && Array.isArray(trace.colorscale)) {
      trace.colorscale = trace.colorscale.map(cs => [ cs[0], mapColorForHeatmapColorscale(cs[1], dark) ]);
    }
    if (trace.coloraxis && fig.layout && fig.layout[trace.coloraxis] && Array.isArray(fig.layout[trace.coloraxis].colorscale)) {
      fig.layout[trace.coloraxis].colorscale =
        fig.layout[trace.coloraxis].colorscale.map(cs => [ cs[0], mapColorForHeatmapColorscale(cs[1], dark) ]);
    }
  }

  function rewriteAnnotations(layout) {
    if (!layout || !Array.isArray(layout.annotations)) return;
    layout.annotations.forEach(a => {
      if (!a) return;
      if (typeof a.bgcolor == "string") {
        a.bgcolor = annbg;
      }
      if (a.font && typeof a.font.color == "string") {
        a.font.color = fg;
      }
    })
  }

  // change Heatmap colorscale in data
  //console.error(`fig.data size=${fig.data.length}`); // DEBUG
  (fig.data || []).forEach(trace => rewriteColorscale(fig, trace, dark));
  // change annotation bgcolor and font.color
  rewriteAnnotations(fig.layout)

  // Notebook-focused layout adjustments:
  // - Transparent backgrounds (let the notebook background show through)
  // - High-contrast text/axes/grid for readability
  fig.layout.paper_bgcolor = "rgba(0,0,0,0)";
  fig.layout.plot_bgcolor  = "rgba(0,0,0,0)";
  fig.layout.font = Object.assign({}, fig.layout.font || {}, { color: fg });

  fig.layout.xaxis = Object.assign({}, fig.layout.xaxis || {}, {
    color: fg,
    gridcolor: grid,
    linecolor: fg,
    tickcolor: fg,
    zerolinecolor: grid
  });

  fig.layout.yaxis = Object.assign({}, fig.layout.yaxis || {}, {
    color: fg,
    gridcolor: grid,
    linecolor: fg,
    tickcolor: fg,
    zerolinecolor: grid
  });

  // console.error("Passed adaptive_plotly.js"); // DEBUG

  // Code for Plotly.newPlot or document.createElement for ERROR should be written on caller side, for it requires {div_id} defined by Python code.

