import re

css = open('frontend/style.css', 'r', encoding='utf-8').read()

# Replace Design Tokens
tokens_start = css.find(':root {')
tokens_end = css.find('}', tokens_start) + 1
new_tokens = """
:root {
  --shadow-sm:    0 2px 8px rgba(0,0,0,0.04);
  --shadow-md:    0 4px 16px rgba(0,0,0,0.06);
  --shadow-lg:    0 10px 30px rgba(0,0,0,0.08);
  --shadow-glow:  0 0 16px var(--accent-dim);

  --radius-sm:    8px;
  --radius-md:    12px;
  --radius-lg:    16px;
  --radius-xl:    20px;

  --sidebar-w:    256px;
  --transition:   0.18s ease;
}

[data-theme="white"] {
  color-scheme: light;
  --bg:           #f5f7fb;
  --bg-2:         #ffffff;
  --panel:        #ffffff;
  --panel-2:      #eef3f8;
  --panel-3:      #e2e8f0;
  --border:       #dce3ec;
  --border-2:     #cbd5e1;
  --text:         #172033;
  --text-2:       #334155;
  --muted:        #667085;
  --muted-2:      #94a3b8;

  --accent:       #0891b2;
  --accent-2:     #0284c7;
  --accent-glow:  rgba(8, 145, 178, 0.15);
  --accent-dim:   rgba(8, 145, 178, 0.08);

  --blue:         #3b82f6;
  --blue-dim:     rgba(59, 130, 246, 0.08);

  --green:        #10b981;
  --amber:        #f59e0b;
  --rose:         #f43f5e;
}

[data-theme="mint"] {
  color-scheme: light;
  --bg:           #f0fdf4;
  --bg-2:         #ffffff;
  --panel:        #ffffff;
  --panel-2:      #dcfce7;
  --panel-3:      #bbf7d0;
  --border:       #bbf7d0;
  --border-2:     #86efac;
  --text:         #064e3b;
  --text-2:       #065f46;
  --muted:        #047857;
  --muted-2:      #059669;

  --accent:       #059669;
  --accent-2:     #047857;
  --accent-glow:  rgba(5, 150, 105, 0.15);
  --accent-dim:   rgba(5, 150, 105, 0.08);

  --blue:         #3b82f6;
  --blue-dim:     rgba(59, 130, 246, 0.08);

  --green:        #10b981;
  --amber:        #f59e0b;
  --rose:         #f43f5e;
}

[data-theme="sky"] {
  color-scheme: light;
  --bg:           #f0f9ff;
  --bg-2:         #ffffff;
  --panel:        #ffffff;
  --panel-2:      #e0f2fe;
  --panel-3:      #bae6fd;
  --border:       #bae6fd;
  --border-2:     #7dd3fc;
  --text:         #0c4a6e;
  --text-2:       #075985;
  --muted:        #0369a1;
  --muted-2:      #0284c7;

  --accent:       #0284c7;
  --accent-2:     #0369a1;
  --accent-glow:  rgba(2, 132, 199, 0.15);
  --accent-dim:   rgba(2, 132, 199, 0.08);

  --blue:         #2563eb;
  --blue-dim:     rgba(37, 99, 235, 0.08);

  --green:        #22c55e;
  --amber:        #f59e0b;
  --rose:         #f43f5e;
}

[data-theme="beige"] {
  color-scheme: light;
  --bg:           #faf9f6;
  --bg-2:         #fdfcfb;
  --panel:        #ffffff;
  --panel-2:      #f3efe6;
  --panel-3:      #eaddc5;
  --border:       #e6dfd3;
  --border-2:     #d6ccbc;
  --text:         #2d2926;
  --text-2:       #4a443f;
  --muted:        #6b635a;
  --muted-2:      #8c8277;

  --accent:       #0f766e;
  --accent-2:     #115e59;
  --accent-glow:  rgba(15, 118, 110, 0.15);
  --accent-dim:   rgba(15, 118, 110, 0.08);

  --blue:         #3b82f6;
  --blue-dim:     rgba(59, 130, 246, 0.08);

  --green:        #16a34a;
  --amber:        #d97706;
  --rose:         #e11d48;
}
"""
css = css[:tokens_start] + new_tokens.strip() + css[tokens_end:]

# Replace hardcoded dark styles
replacements = {
    'color: #93c5fd;': 'color: var(--blue);',
    'background: rgba(96, 165, 250, 0.1);': 'background: var(--blue-dim);',
    'color: #5a7a9a;': 'color: var(--accent);',
    'background: linear-gradient(135deg, #101d2e 0%, #0d1624 60%, #08111c 100%);': 'background: var(--panel);',
    'background: radial-gradient(circle, rgba(34,211,238,0.06) 0%, transparent 70%);': 'background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);',
    'border: 1px solid rgba(34,211,238,0.3);': 'border: 1px solid var(--accent);',
    'color: rgba(34,211,238,0.7);': 'color: var(--accent);',
    'background: linear-gradient(135deg, #0e1d30 0%, #101828 100%);': 'background: var(--panel-2);',
    'border-color: rgba(34,211,238,0.15);': 'border-color: var(--border-2);',
    'color: #a8bbd0;': 'color: var(--text-2);',
    'background: #05101a;': 'background: var(--bg);',
    'color: #6da4d4;': 'color: var(--accent);',
    'background: linear-gradient(135deg, #101d30, #0d1624);': 'background: var(--panel);',
    'background: #07111e;': 'background: var(--panel-2);',
    'border-color: rgba(34,211,238,0.2);': 'border-color: var(--accent-glow);',
    'border-color: rgba(96,165,250,0.2);': 'border-color: var(--blue-dim);',
    'background: rgba(34,211,238,0.05);': 'background: var(--accent-dim);',
    'border-color: rgba(34,211,238,0.35);': 'border-color: var(--accent-glow);',
    'border-color: rgba(96,165,250,0.3);': 'border-color: var(--blue-dim);',
    'background: rgba(34,211,238,0.06);': 'background: var(--accent-dim);',
    'rgba(255,255,255,0.025)': 'var(--panel-2)',
}

for old, new in replacements.items():
    css = css.replace(old, new)

# Add theme selector CSS at the bottom
theme_selector_css = """
/* ══════════════════════════════════════════════════════════════
   THEME SELECTOR
══════════════════════════════════════════════════════════════ */
.theme-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--panel);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}

.theme-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 6px;
  font-size: 16px;
  line-height: 1;
  transition: var(--transition);
  opacity: 0.6;
}

.theme-btn:hover {
  opacity: 1;
  background: var(--panel-2);
}

.theme-btn.active {
  opacity: 1;
  background: var(--panel-3);
  box-shadow: inset 0 0 0 1px var(--border-2);
}
"""
css += theme_selector_css

with open('frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('Updated style.css')
