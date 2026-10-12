import re

js = open('frontend/script.js', 'r', encoding='utf-8').read()

# 1. Update PALETTE to be dynamic
palette_old = """const PALETTE = {
  cyan:    '#22d3ee',
  blue:    '#60a5fa',
  violet:  '#a78bfa',
  amber:   '#fbbf24',
  green:   '#4ade80',
  rose:    '#fb7185',
  sky:     '#38bdf8',
  teal:    '#2dd4bf',
};"""

palette_new = """function getPalette() {
  const style = getComputedStyle(document.documentElement);
  const getVar = (name, fallback) => style.getPropertyValue(name).trim() || fallback;
  return {
    cyan:    getVar('--accent', '#0891b2'),
    blue:    getVar('--blue', '#3b82f6'),
    violet:  getVar('--text-2', '#334155'),
    amber:   getVar('--amber', '#f59e0b'),
    green:   getVar('--green', '#10b981'),
    rose:    getVar('--rose', '#f43f5e'),
    sky:     getVar('--accent-2', '#0284c7'),
    teal:    getVar('--muted', '#667085'),
  };
}"""
js = js.replace(palette_old, palette_new)

# 2. Update drawAllCharts to use dynamic palette
drawAllCharts_old = """function drawAllCharts(rows) {
  if (!rows || rows.length === 0) {
    ['chartEncDec','chartTxTime','chartThroughput','chartTotal','chartCpuMem'].forEach(id => {
      drawGroupedBarChart(id, [], []);
    });
    return;
  }

  const labels = rows.map(makeKBLabel);

  // 1. Encryption vs Decryption Time
  drawGroupedBarChart('chartEncDec', labels, [
    { label: 'Encryption (ms)',  values: rows.map(r => flt(r, COL.encTimeMean)),  color: PALETTE.cyan   },
    { label: 'Decryption (ms)',  values: rows.map(r => flt(r, COL.decTimeMean)),  color: PALETTE.blue   },
  ], 'ms');

  // 2. Plaintext vs Encrypted Transmission
  drawGroupedBarChart('chartTxTime', labels, [
    { label: 'Plain TX (ms)',    values: rows.map(r => flt(r, COL.plainTxMean)),  color: PALETTE.teal   },
    { label: 'Encrypted TX (ms)',values: rows.map(r => flt(r, COL.encTxMean)),    color: PALETTE.violet },
  ], 'ms');

  // 3. Throughput comparison
  drawGroupedBarChart('chartThroughput', labels, [
    { label: 'Plain (Mbps)',     values: rows.map(r => flt(r, COL.plainMbps)),    color: PALETTE.green  },
    { label: 'Encrypted (Mbps)',values: rows.map(r => flt(r, COL.encMbps)),       color: PALETTE.amber  },
  ], 'Mbps');

  // 4. Encrypted Total Time
  drawGroupedBarChart('chartTotal', labels, [
    { label: 'Encrypted Total (ms)', values: rows.map(r => flt(r, COL.totalMean)), color: PALETTE.rose  },
  ], 'ms');

  // 5. CPU & Memory
  drawGroupedBarChart('chartCpuMem', labels, [
    { label: 'CPU (%)',          values: rows.map(r => flt(r, COL.cpuMean)),       color: PALETTE.sky    },
    { label: 'Memory (%)',       values: rows.map(r => flt(r, COL.memMean)),       color: PALETTE.violet },
  ], '%');
}"""

drawAllCharts_new = """function drawAllCharts(rows) {
  if (!rows || rows.length === 0) {
    ['chartEncDec','chartTxTime','chartThroughput','chartTotal','chartCpuMem'].forEach(id => {
      drawGroupedBarChart(id, [], []);
    });
    return;
  }

  const labels = rows.map(makeKBLabel);
  const PALETTE = getPalette();

  // 1. Encryption vs Decryption Time
  drawGroupedBarChart('chartEncDec', labels, [
    { label: 'Encryption (ms)',  values: rows.map(r => flt(r, COL.encTimeMean)),  color: PALETTE.cyan   },
    { label: 'Decryption (ms)',  values: rows.map(r => flt(r, COL.decTimeMean)),  color: PALETTE.blue   },
  ], 'ms');

  // 2. Plaintext vs Encrypted Transmission
  drawGroupedBarChart('chartTxTime', labels, [
    { label: 'Plain TX (ms)',    values: rows.map(r => flt(r, COL.plainTxMean)),  color: PALETTE.teal   },
    { label: 'Encrypted TX (ms)',values: rows.map(r => flt(r, COL.encTxMean)),    color: PALETTE.violet },
  ], 'ms');

  // 3. Throughput comparison
  drawGroupedBarChart('chartThroughput', labels, [
    { label: 'Plain (Mbps)',     values: rows.map(r => flt(r, COL.plainMbps)),    color: PALETTE.green  },
    { label: 'Encrypted (Mbps)',values: rows.map(r => flt(r, COL.encMbps)),       color: PALETTE.amber  },
  ], 'Mbps');

  // 4. Encrypted Total Time
  drawGroupedBarChart('chartTotal', labels, [
    { label: 'Encrypted Total (ms)', values: rows.map(r => flt(r, COL.totalMean)), color: PALETTE.rose  },
  ], 'ms');

  // 5. CPU & Memory
  drawGroupedBarChart('chartCpuMem', labels, [
    { label: 'CPU (%)',          values: rows.map(r => flt(r, COL.cpuMean)),       color: PALETTE.sky    },
    { label: 'Memory (%)',       values: rows.map(r => flt(r, COL.memMean)),       color: PALETTE.violet },
  ], '%');
}"""
js = js.replace(drawAllCharts_old, drawAllCharts_new)

# Replace dark colors in chart rendering logic
js = js.replace("ctx.fillStyle = '#5a6878';", "ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--muted-2').trim();")
js = js.replace("ctx.strokeStyle = 'rgba(30,45,66,0.9)';", "ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--border').trim();")
js = js.replace("ctx.fillStyle = '#7a8899';", "ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--muted').trim();")
js = js.replace("ctx.fillStyle = '#c5ced9';", "ctx.fillStyle = '#ffffff';")
js = js.replace("ctx.fillStyle = '#8d98a9';", "ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--muted').trim();")

# Add theme switcher logic
theme_logic = """
/* ══════════════════════════════════════════════════════════════
   THEME SWITCHER
══════════════════════════════════════════════════════════════ */
const themeBtns = document.querySelectorAll('.theme-btn');

function applyTheme(theme) {
  if (!['white', 'mint', 'sky', 'beige'].includes(theme)) {
    theme = 'white';
  }
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('cryptonet-theme', theme);
  
  themeBtns.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.setTheme === theme);
  });

  // Redraw charts so they pick up new colors from CSS vars
  if (allRows && allRows.length > 0) {
    drawAllCharts(allRows);
  }
}

themeBtns.forEach(btn => {
  btn.addEventListener('click', () => applyTheme(btn.dataset.setTheme));
});

// Initialize Theme
const savedTheme = localStorage.getItem('cryptonet-theme') || 'white';
applyTheme(savedTheme);
"""

# Append theme logic to the bottom of the script
if "THEME SWITCHER" not in js:
    js += theme_logic

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Updated script.js')
