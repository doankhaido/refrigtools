// Refrigerant Handling Field Tool — offline PWA
// Code of Practice 2025 Edition Parts 1 & 2

const REFRIGERANTS = {
  "R32":   { type:"HFC", name:"Difluoromethane", gwp_au:675, gwp_nz:771, safety:"A2L", flam:true, fr:0.78, lfl_pct:14.4, lfl_gm3:307, density57:0.795, adg:"2.1 Flammable", odp:0, scheduled:true },
  "R134a": { type:"HFC", name:"1,1,1,2-Tetrafluoroethane", gwp_au:1430, gwp_nz:1300, safety:"A1", flam:false, fr:1.04, density57:1.072, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R125":  { type:"HFC", name:"Pentafluoroethane", gwp_au:3500, gwp_nz:3170, safety:"A1", flam:false, density57:0.91, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R143a": { type:"HFC", name:"1,1,1-Trifluoroethane", gwp_au:4470, gwp_nz:4800, safety:"A2L", flam:true, adg:"2.1 Flammable", odp:0, scheduled:true },
  "R152a": { type:"HFC", name:"1,1-Difluoroethane", gwp_au:124, gwp_nz:138, safety:"A2", flam:true, adg:"2.1 Flammable", odp:0, scheduled:true },
  "R23":   { type:"HFC", name:"Trifluoromethane", gwp_au:14800, gwp_nz:12400, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R22":   { type:"HCFC", name:"Chlorodifluoromethane", gwp_au:1810, gwp_nz:1760, safety:"A1", flam:false, fr:1.03, density57:1.054, adg:"2.2 Non-flammable", odp:0.055, scheduled:true },
  "R123":  { type:"HCFC", name:"Dichlorotrifluoroethane", gwp_au:77, gwp_nz:79, safety:"B1", flam:false, adg:"2.2 Non-flammable", odp:0.02, scheduled:true },
  "R404A": { type:"Blend", name:"HFC-125/134a/143a (44/4/52%)", gwp_au:3922, gwp_nz:3943, safety:"A1", flam:false, fr:0.82, density57:0.846, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R407C": { type:"Blend", name:"HFC-32/125/134a (23/25/52%)", gwp_au:1774, gwp_nz:1624, safety:"A1", flam:false, fr:0.94, density57:0.969, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R407F": { type:"Blend", name:"HFC-32/125/134a (30/30/40%)", gwp_au:1825, gwp_nz:1674, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R410A": { type:"Blend", name:"HFC-32/125 (50/50%)", gwp_au:2088, gwp_nz:1924, safety:"A1", flam:false, fr:0.82, density57:0.846, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R448A": { type:"Blend", name:"HFC/HFO blend (5 components)", gwp_au:1386, gwp_nz:1273, safety:"A1", flam:false, fr:0.90, density57:0.928, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R449A": { type:"Blend", name:"HFC/HFO blend (4 components)", gwp_au:1396, gwp_nz:1282, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R450A": { type:"Blend", name:"HFC-134a/HFO-1234yf (42/58%)", gwp_au:601, gwp_nz:547, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R452A": { type:"Blend", name:"HFC-32/125/HFO-1234yf (11/59/30%)", gwp_au:2139, gwp_nz:1945, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R454B": { type:"Blend", name:"HFC-32/HFO-1234yf (68.9/31.1%)", gwp_au:466, gwp_nz:466, safety:"A2L", flam:true, fr:0.82, lfl_pct:11.3, lfl_gm3:303, density57:0.846, adg:"2.1 Flammable", odp:0, scheduled:true },
  "R454C": { type:"Blend", name:"HFC-32/HFO-1234yf (21.5/78.5%)", gwp_au:148, gwp_nz:148, safety:"A2L", flam:true, fr:0.89, density57:0.918, adg:"2.1 Flammable", odp:0, scheduled:true },
  "R507A": { type:"Blend", name:"HFC-125/143a (50/50%)", gwp_au:3985, gwp_nz:3985, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R513A": { type:"Blend", name:"HFC-134a/HFO-1234yf (44/56%)", gwp_au:629, gwp_nz:573, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R515B": { type:"Blend", name:"HFO-1234ze/HFC-227ea (91.1/8.9%)", gwp_au:299, gwp_nz:299, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:true },
  "R1234yf":{ type:"HFO", name:"2,3,3,3-Tetrafluoropropene", gwp_au:4, gwp_nz:1, safety:"A2L", flam:true, lfl_pct:6.2, lfl_gm3:289, adg:"2.1 Flammable", odp:0, scheduled:false },
  "R1234ze":{ type:"HFO", name:"trans-1,3,3,3-Tetrafluoropropene", gwp_au:7, gwp_nz:1, safety:"A2L", flam:true, lfl_pct:6.5, lfl_gm3:303, adg:"2.1 Flammable", odp:0, scheduled:false },
  "R290":  { type:"HC", name:"Propane", gwp_au:3, gwp_nz:0, safety:"A3", flam:true, lfl_pct:2.1, lfl_gm3:38, adg:"2.1 Flammable", odp:0, scheduled:false },
  "R600a": { type:"HC", name:"Isobutane", gwp_au:3, gwp_nz:0, safety:"A3", flam:true, lfl_pct:1.8, lfl_gm3:43, adg:"2.1 Flammable", odp:0, scheduled:false },
  "R1270": { type:"HC", name:"Propylene", gwp_au:3, gwp_nz:0, safety:"A3", flam:true, lfl_pct:2.0, lfl_gm3:36, adg:"2.1 Flammable", odp:0, scheduled:false },
  "R744":  { type:"Natural", name:"Carbon dioxide", gwp_au:1, gwp_nz:1, safety:"A1", flam:false, adg:"2.2 Non-flammable", odp:0, scheduled:false, hp:true },
  "R717":  { type:"Natural", name:"Ammonia", gwp_au:0, gwp_nz:0, safety:"B2L", flam:true, lfl_pct:15, lfl_gm3:116, adg:"2.3 Toxic", odp:0, scheduled:false, toxic:true },
  "R718":  { type:"Natural", name:"Water", gwp_au:0, gwp_nz:0, safety:"A1", flam:false, adg:"Not regulated", odp:0, scheduled:false }
};

const PROCEDURES = {
  "evac-deep": {
    title: "Deep evacuation",
    sub: "Suitable for small simple systems with low contamination risk",
    steps: [
      "Recover all scheduled refrigerant before evacuation",
      "Depressurise system fully — do not introduce air",
      "Connect dedicated evacuation hoses (large diameter, short)",
      "Evacuate to ≤ 500 μm / 67 Pa absolute",
      "Isolate vacuum pump from system",
      "Allow to stand 60 minutes — vacuum must stay below 600 μm / 80 Pa",
      "Drop test: rise ≤ 100 μm in 1 hour = pass",
      "If gauge rises ≥ 100 μm — leak test, repair, retest"
    ],
    note: "Use a dedicated vacuum gauge, not a manifold pressure gauge. Below 0 °C dehydration takes much longer; below 4,500 μm moisture can ice."
  },
  "evac-triple": {
    title: "Triple evacuation",
    sub: "Required for large/complex systems and pipework exposed to atmosphere",
    steps: [
      "Recover all scheduled refrigerant",
      "Pull first vacuum to ≤ 4,500 μm / 600 Pa absolute",
      "Break vacuum with oxygen-free nitrogen (OFN)",
      "Allow system to stand, then purge OFN through pipework",
      "Pull second vacuum to ≤ 4,500 μm / 600 Pa absolute",
      "Break with OFN again",
      "Pull third vacuum to ≤ 500 μm / 67 Pa absolute",
      "Isolate pump, stand 60 min, vacuum must stay below 600 μm",
      "Drop test: rise ≤ 100 μm in 1 hour = pass"
    ],
    note: "Never use scheduled refrigerant to break vacuum or test for leaks. OFN only."
  },
  "leak-test": {
    title: "Leak tightness test (OFN)",
    sub: "Required at commissioning, after repair, after refrigerant change, after >2 yr standstill",
    steps: [
      "Evacuate system; recover refrigerant if present",
      "Connect OFN cylinder (use tracer gas H₂/N₂ <5% for higher sensitivity)",
      "Pressurise in stages — check each increment",
      "Reach test pressure: maximum allowable PS (commissioning) or 25–90% PS (repair)",
      "Isolate from cylinder; record system pressure and ambient temperature",
      "Hold: 24 hours commissioning / 1 hour repair",
      "Test all potential leak points with electronic detector",
      "Acceptance: GWP > 150 → no leaks at 10⁻⁶ Pa·m³/s; GWP < 150 → 10⁻³ Pa·m³/s",
      "Leak found → vent OFN, repair, retest"
    ],
    warn: "OFN test pressures can cause serious injury. Nitrogen is an asphyxiant. Never use standard-grade nitrogen (oxygen risk at high pressure). Never pressure-test with refrigerant."
  },
  "charge": {
    title: "Refrigerant charging",
    sub: "Field charging after repair or recommissioning — charge by mass when possible",
    steps: [
      "Confirm system has been evacuated to spec and passed drop test",
      "Verify refrigerant matches identification plate",
      "Connect cylinder; partially open valve to pressurise hose",
      "Leak-test hose connection before fully opening cylinder",
      "Weigh refrigerant in and out of system (AS 4211.3)",
      "Charge per AS/NZS 5149.4 §C.2 — blends as liquid only",
      "Do not exceed system RCL or identification plate quantity",
      "Record quantity in logbook (≥3 kg systems)"
    ],
    warn: "Flammable refrigerant: assess area as temporary flammable zone. Earth system before charging. Remove ignition sources. Use rated tools."
  },
  "recovery": {
    title: "Refrigerant recovery",
    sub: "All scheduled refrigerant must be recovered — never vented",
    steps: [
      "Use recovery unit conforming to AS 4211.3 / ISO 11650 / AHRI 740",
      "Use cylinder appropriate for refrigerant (AS 4484, AS 2030.1, AS/NZS 1200)",
      "Check cylinder test stamp date — not expired",
      "Flammable refrigerant → A2/A2L-rated cylinder and equipment",
      "Recover both vapour and liquid — full charge",
      "Do not exceed cylinder fill ratio (see Calc → Safe fill)",
      "Do not mix contaminated and clean refrigerant in one cylinder",
      "Refrigerant unable to be identified → treat as flammable + toxic",
      "Send for recycling, reclamation (AHRI 700) or destruction"
    ],
    note: "AU: Refrigerant Handling Licence required. Refrigerant Trading Authorisation needed for bulk. NZ: Refrigerant Fillers Certificate for refilling cylinders."
  },
  "decom": {
    title: "Decommissioning",
    sub: "End-of-life recovery and labelling",
    steps: [
      "Recover all scheduled refrigerant from every part of system",
      "Send recovered refrigerant for reclamation or disposal",
      "Label equipment: 'Decommissioned and emptied of refrigerant'",
      "Date and sign the label",
      "For fridges/freezers: remove or disable locks",
      "Remove or disable doors/drawers/lids if accessible to public",
      "Update system documentation"
    ]
  }
};

const INFO = {
  "label-new": {
    title: "Identification plate — required fields",
    body: `<ul>
      <li>Name or identification of supplier/manufacturer</li>
      <li>Model, serial number, or reference number</li>
      <li>Year of manufacture (may be coded in serial)</li>
      <li>Refrigerant designation per AS/NZS ISO 817</li>
      <li>Refrigerant charge</li>
      <li>Maximum allowable pressure (high and low side)</li>
      <li>For flammable refrigerants: flame symbol ISO 7010 W021</li>
    </ul>`,
    src: "AS/NZS 5149.2 §5.4 — Part 1 §5.1 / Part 2 §7.2.1"
  },
  "label-change": {
    title: "Refrigerant or lubricant change label",
    body: `<ul>
      <li>New refrigerant designation (AS/NZS ISO 817)</li>
      <li>Refrigerant charge</li>
      <li>Maximum allowable pressure (high and low side)</li>
      <li>Flame symbol if flammable</li>
      <li>Technician name</li>
      <li>Licence number — Australia only</li>
      <li>Service organisation</li>
      <li>Date of change</li>
      <li>Whether UV dye has been added</li>
      <li>If lubricant changed: lubricant type</li>
    </ul>`,
    src: "Code §5.2 (Part 1) / §7.2.2 (Part 2)"
  },
  "logbook": {
    title: "Logbook — systems ≥ 3 kg charge",
    body: `<ul>
      <li>Maintenance and repair work performed</li>
      <li>Quantity and kind of refrigerant charged or removed (new, reused, recycled) each occasion</li>
      <li>Source and analysis results of any reused refrigerant</li>
      <li>All component changes and replacements</li>
      <li>Periodic routine test results</li>
      <li>Significant non-use periods</li>
    </ul>`,
    src: "AS/NZS 5149.2 — Code §7.4 (Part 2)"
  },
  "leak-detect": {
    title: "Leak detection methods",
    body: `<ul>
      <li><strong>Electronic detector</strong> — must be specific to refrigerant type. Recommended primary method. Sensitivity ≥ 5 g/yr.</li>
      <li><strong>Ultrasonic</strong> — detects sound of leaking gas</li>
      <li><strong>UV additive</strong> — fluorescent dye + UV light</li>
      <li><strong>Leak detection spray</strong> — point-source verification only</li>
    </ul>
    <div class="danger">Halide detectors create sparks — must not be used with flammable refrigerants. Use combustible-gas detectors only.</div>`,
    src: "Code §8.5.3 (Part 1) / §4.9.3 (Part 2)"
  },
  "prohibited": {
    title: "Prohibited refrigerant charging",
    body: `<ul>
      <li>Cannot charge with higher GWP than design refrigerant</li>
      <li>Exception: original was an ozone-depleting HCFC</li>
      <li>Cannot charge a non-scheduled-refrigerant system with a scheduled refrigerant</li>
      <li>Cannot top up known/suspected leaking system before repair</li>
    </ul>
    <div class="warn">Australian regulations 2AAA, 111A, 135, 141. Offence under the Act.</div>`,
    src: "Code §1.2.2"
  },
  "discharge": {
    title: "Banned discharge practices",
    body: `<ul>
      <li>Venting refrigerant directly or indirectly to atmosphere</li>
      <li>Charging into equipment with known/suspected leaks</li>
      <li>Using refrigerant to flush pipework internally</li>
      <li>Using refrigerant as the pressure medium for leak testing</li>
      <li>Using refrigerant to clean heat exchanger fins/coils</li>
    </ul>
    <div class="danger">AU: §45B Ozone Protection and Synthetic Greenhouse Gas Management Act 1989. NZ: Ozone Layer Protection Act 1996 + Climate Change Response Act 2002.</div>`,
    src: "Code §1.2.1"
  },
  "competent": {
    title: "Who can do the work",
    body_au: `<ul>
      <li>Refrigerant Handling Licence required for any handling of scheduled refrigerant</li>
      <li>Trainee licence + supervision for apprentices</li>
      <li>Refrigerant Trading Authorisation for bulk acquisition/possession/disposal</li>
      <li>RTA holders and some RHL holders must show permit number on advertising, invoices, receipts, quotes</li>
      <li>Permit holders must comply with all permit conditions</li>
    </ul>`,
    body_nz: `<ul>
      <li>Refrigerant filler and handler training and certification required</li>
      <li>Filler compliance certificate required for filling pressurised gas containers (any gas, including air)</li>
      <li>Refrigerant License New Zealand (RLNZ) provides training and certification</li>
      <li>Cylinders inspected every 5 years from manufacture</li>
    </ul>`,
    src: "Code §1.1"
  }
};

let jurisdiction = localStorage.getItem('juris') || 'AU';

function setJurisdiction(j) {
  jurisdiction = j;
  localStorage.setItem('juris', j);
  document.getElementById('j-au').classList.toggle('active', j === 'AU');
  document.getElementById('j-nz').classList.toggle('active', j === 'NZ');
  renderRefDetail();
  renderInfo();
  renderTool();
  renderCalc();
}
document.getElementById('j-au').onclick = () => setJurisdiction('AU');
document.getElementById('j-nz').onclick = () => setJurisdiction('NZ');

document.querySelectorAll('.tab-btn').forEach(b => {
  b.onclick = () => {
    document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById('panel-' + b.dataset.tab).classList.add('active');
  };
});

const refSelect = document.getElementById('ref-select');
const refSearch = document.getElementById('ref-search');
function populateRefSelect(filter) {
  refSelect.innerHTML = '';
  const f = (filter || '').toLowerCase();
  Object.keys(REFRIGERANTS).forEach(k => {
    const r = REFRIGERANTS[k];
    if (f && !k.toLowerCase().includes(f) && !r.name.toLowerCase().includes(f) && !r.type.toLowerCase().includes(f)) return;
    const opt = document.createElement('option');
    opt.value = k;
    opt.textContent = k + (r.scheduled ? '' : ' *') + ' — ' + r.name;
    refSelect.appendChild(opt);
  });
}
populateRefSelect();
refSearch.oninput = () => { populateRefSelect(refSearch.value); renderRefDetail(); };

function safetyColor(s) {
  if (s === 'A1') return ['var(--bg-success)', 'var(--text-success)'];
  if (s === 'A2L' || s === 'B2L') return ['var(--bg-warning)', 'var(--text-warning)'];
  if (s === 'A2' || s === 'A3' || s.startsWith('B')) return ['var(--bg-danger)', 'var(--text-danger)'];
  return ['var(--bg-secondary)', 'var(--text-secondary)'];
}

function renderRefDetail() {
  if (!refSelect.value) { document.getElementById('ref-detail').innerHTML = '<div class="note">No refrigerants match.</div>'; return; }
  const k = refSelect.value;
  const r = REFRIGERANTS[k];
  const gwp = jurisdiction === 'AU' ? r.gwp_au : r.gwp_nz;
  const gwpSrc = jurisdiction === 'AU' ? 'AR4 (AU)' : 'AR5 (NZ)';
  const [bg, fg] = safetyColor(r.safety);
  let html = `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 8px;">
        <div style="min-width: 0;">
          <div style="font-size: 18px; font-weight: 500;">${k}${!r.scheduled ? ' <span style="font-size: 11px; color: var(--text-tertiary); font-weight: 400;">non-scheduled</span>' : ''}</div>
          <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.4;">${r.name}</div>
        </div>
        <span class="pill" style="background: ${bg}; color: ${fg};">${r.safety}</span>
      </div>
      <div class="kv"><span class="kv-k">Type</span><span class="kv-v">${r.type}</span></div>
      <div class="kv"><span class="kv-k">GWP (${gwpSrc})</span><span class="kv-v">${gwp.toLocaleString()}</span></div>
      <div class="kv"><span class="kv-k">ODP</span><span class="kv-v">${r.odp}</span></div>
      <div class="kv"><span class="kv-k">ADG transport</span><span class="kv-v">${r.adg}</span></div>
      ${r.fr ? `<div class="kv"><span class="kv-k">Fill ratio</span><span class="kv-v">${r.fr.toFixed(2)}</span></div>` : ''}
      ${r.lfl_pct ? `<div class="kv"><span class="kv-k">LFL</span><span class="kv-v">${r.lfl_pct}% / ${r.lfl_gm3} g/m³</span></div>` : ''}
    </div>
  `;
  if (!r.scheduled) html += '<div class="note"><strong>Outside the scope of this code.</strong> Non-scheduled refrigerant — additional licencing or safety requirements may apply (HWSA, AIRAH guides).</div>';
  if (r.flam) html += '<div class="warn"><strong>Flammable refrigerant.</strong> Tools must be rated for flammability grade. Earth system before charging. Remove ignition sources. Use combustible-gas leak detector.</div>';
  if (r.toxic) html += '<div class="danger"><strong>Toxic.</strong> Class B refrigerant. Occupational exposure limit < 400 ppm. Use SCBA and oxygen monitor in enclosed spaces.</div>';
  if (r.hp) html += '<div class="warn"><strong>High-pressure refrigerant.</strong> Use rated recovery cylinders only.</div>';
  if (r.type === 'HCFC') html += '<div class="warn"><strong>Ozone-depleting HCFC.</strong> Phase-out applies.</div>';
  document.getElementById('ref-detail').innerHTML = html;
}
refSelect.onchange = renderRefDetail;

let currentCalc = 'sfc';
document.querySelectorAll('#calc-tabs button').forEach(b => {
  b.onclick = () => {
    document.querySelectorAll('#calc-tabs button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    currentCalc = b.dataset.calc;
    renderCalc();
  };
});

function renderCalc() {
  const body = document.getElementById('calc-body');
  if (currentCalc === 'sfc') {
    const opts = Object.keys(REFRIGERANTS).filter(k => REFRIGERANTS[k].fr).map(k => `<option value="${k}">${k}</option>`).join('');
    body.innerHTML = `
      <div class="row"><label>Refrigerant</label><select id="sfc-ref">${opts}</select></div>
      <div class="row"><label>Water cap. (L)</label><input id="sfc-wc" type="number" value="13.6" step="0.1" /></div>
      <div class="row"><label>Use case</label><select id="sfc-mode"><option value="new">New (3% ullage)</option><option value="rec">Recovered (20% ullage)</option></select></div>
      <div class="metric"><div class="metric-l">Safe fill capacity</div><div class="metric-v" id="sfc-out">—</div><div class="metric-s" id="sfc-formula">—</div></div>
      <div class="note">SFC = FR × WC for new (AS 2030.5). For recovered, SFC = 0.80 × FR × WC (AS 4211.3 — 20% ullage). Never exceed cylinder maximum gross weight.</div>
    `;
    const upd = () => {
      const k = document.getElementById('sfc-ref').value;
      const wc = parseFloat(document.getElementById('sfc-wc').value) || 0;
      const mode = document.getElementById('sfc-mode').value;
      const fr = REFRIGERANTS[k].fr;
      const sfc = mode === 'new' ? fr * wc : 0.80 * fr * wc;
      document.getElementById('sfc-out').textContent = sfc.toFixed(2) + ' kg';
      document.getElementById('sfc-formula').textContent = mode === 'new' ? `${fr.toFixed(2)} × ${wc} L` : `0.80 × ${fr.toFixed(2)} × ${wc} L`;
    };
    document.getElementById('sfc-ref').onchange = upd;
    document.getElementById('sfc-wc').oninput = upd;
    document.getElementById('sfc-mode').onchange = upd;
    upd();
  } else if (currentCalc === 'leak') {
    const opts = Object.keys(REFRIGERANTS).filter(k => REFRIGERANTS[k].scheduled).map(k => `<option value="${k}">${k} (GWP ${jurisdiction === 'AU' ? REFRIGERANTS[k].gwp_au : REFRIGERANTS[k].gwp_nz})</option>`).join('');
    body.innerHTML = `
      <div class="row"><label>System</label><select id="lk-sys"><option value="self">Self-contained / Unit</option><option value="herm">Hermetic ≤6 kg</option><option value="other">Other system</option></select></div>
      <div class="row"><label>Charge (kg)</label><input id="lk-kg" type="number" value="50" step="1" /></div>
      <div class="row"><label>Refrigerant</label><select id="lk-ref">${opts}</select></div>
      <div class="row"><label>Fixed detect.</label><select id="lk-det"><option value="no">No</option><option value="yes">Yes</option></select></div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <div class="metric"><div class="metric-l">AS/NZS 5149.4</div><div class="metric-v" id="lk-as">—</div><div class="metric-s">Mandatory min</div></div>
        <div class="metric"><div class="metric-l">EU F-Gas</div><div class="metric-v" id="lk-eu">—</div><div class="metric-s" id="lk-eu-s">tCO₂e</div></div>
      </div>
      <div class="note">EU F-Gas tiers use tonnes CO₂-equivalent. For HFOs the tiers are mass-based.</div>
    `;
    const upd = () => {
      const sys = document.getElementById('lk-sys').value;
      const kg = parseFloat(document.getElementById('lk-kg').value) || 0;
      const k = document.getElementById('lk-ref').value;
      const det = document.getElementById('lk-det').value === 'yes';
      const r = REFRIGERANTS[k];
      const gwp = jurisdiction === 'AU' ? r.gwp_au : r.gwp_nz;
      let asTxt = '—';
      if (sys === 'self') asTxt = 'After repair';
      else if (sys === 'herm') asTxt = kg <= 6 ? '12 months' : 'n/a';
      else {
        if (kg <= 3) asTxt = 'After repair';
        else if (kg <= 30) asTxt = '12 months';
        else if (kg <= 300) asTxt = '6 months';
        else asTxt = '3 months';
      }
      document.getElementById('lk-as').textContent = asTxt;
      const isHFO = r.type === 'HFO' || (k === 'R450A');
      let euTxt = '—', euSub = 'tCO₂e tier';
      if (isHFO) {
        euSub = 'HFO mass tier';
        if (kg < 1) euTxt = 'n/a';
        else if (kg < 10) euTxt = det ? '24 mo' : '12 mo';
        else if (kg < 100) euTxt = det ? '12 mo' : '6 mo';
        else euTxt = det ? '6 mo' : '3 mo';
      } else {
        const tco2 = (kg * gwp) / 1000;
        euSub = tco2.toFixed(1) + ' tCO₂e';
        if (tco2 < 5) euTxt = 'n/a';
        else if (tco2 < 50) euTxt = det ? '24 mo' : '12 mo';
        else if (tco2 < 500) euTxt = det ? '12 mo' : '6 mo';
        else euTxt = det ? '6 mo' : '3 mo';
      }
      document.getElementById('lk-eu').textContent = euTxt;
      document.getElementById('lk-eu-s').textContent = euSub;
    };
    document.getElementById('lk-sys').onchange = upd;
    document.getElementById('lk-kg').oninput = upd;
    document.getElementById('lk-ref').onchange = upd;
    document.getElementById('lk-det').onchange = upd;
    upd();
  } else if (currentCalc === 'drop') {
    body.innerHTML = `
      <div class="row"><label>Initial (μm)</label><input id="dt-i" type="number" value="500" step="10" /></div>
      <div class="row"><label>After 1 hr (μm)</label><input id="dt-f" type="number" value="580" step="10" /></div>
      <div class="metric"><div class="metric-l">Rise</div><div class="metric-v" id="dt-rise">—</div><div class="metric-s" id="dt-result">—</div></div>
      <div class="note">Per AS/NZS 5149.4: vacuum should not rise more than 100 μm (13.33 Pa) in 1 hour.</div>
    `;
    const upd = () => {
      const i = parseFloat(document.getElementById('dt-i').value) || 0;
      const f = parseFloat(document.getElementById('dt-f').value) || 0;
      const rise = f - i;
      document.getElementById('dt-rise').textContent = rise + ' μm';
      const out = document.getElementById('dt-result');
      const card = out.parentElement;
      if (rise <= 100 && rise >= 0) { out.textContent = 'PASS — within limit'; card.style.background = 'var(--bg-success)'; out.style.color = 'var(--text-success)'; }
      else if (rise < 0) { out.textContent = 'Re-check gauge'; card.style.background = 'var(--bg-secondary)'; out.style.color = 'var(--text-secondary)'; }
      else { out.textContent = 'FAIL — leak or moisture'; card.style.background = 'var(--bg-danger)'; out.style.color = 'var(--text-danger)'; }
    };
    document.getElementById('dt-i').oninput = upd;
    document.getElementById('dt-f').oninput = upd;
    upd();
  } else if (currentCalc === 'torq') {
    body.innerHTML = `
      <div class="note" style="margin-top:0;">Single-flare torque — copper tube, AS/NZS 5149.2 Table 4.</div>
      <table class="tbl">
        <thead><tr><th>OD (mm)</th><th>(in)</th><th>Wall</th><th>N·m</th></tr></thead>
        <tbody>
          <tr><td>6 / 6.35</td><td>1/4</td><td>0.80</td><td>14 – 18</td></tr>
          <tr><td>7.94</td><td>5/16</td><td>0.80</td><td>33 – 42</td></tr>
          <tr><td>8 / 9.52 / 10</td><td>3/8</td><td>0.80</td><td>33 – 42</td></tr>
          <tr><td>12 / 12.7</td><td>1/2</td><td>0.80</td><td>50 – 62</td></tr>
          <tr><td>15 / 15.88</td><td>5/8</td><td>0.80–0.95</td><td>63 – 77</td></tr>
          <tr><td>18 / 19.06</td><td>3/4</td><td>1.00</td><td>90 – 110</td></tr>
        </tbody>
      </table>
      <div class="warn">Use a torque wrench. Lubricate flare with refrigerant-compatible lubricant.</div>
    `;
  }
}

let currentTool = 'room';
document.querySelectorAll('#tool-tabs button').forEach(b => {
  b.onclick = () => {
    document.querySelectorAll('#tool-tabs button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    currentTool = b.dataset.tool;
    renderTool();
  };
});

function renderTool() {
  const body = document.getElementById('tool-body');
  if (currentTool === 'room') {
    const opts = Object.keys(REFRIGERANTS).filter(k => REFRIGERANTS[k].lfl_gm3 && REFRIGERANTS[k].safety.endsWith('2L')).map(k => `<option value="${k}">${k}</option>`).join('');
    body.innerHTML = `
      <div class="note" style="margin-top:0;">Simplified AS/NZS 60335.2.40 Annex GG estimate. <strong>Use the manufacturer's stated minimum room area for the actual install.</strong></div>
      <div class="row"><label>Refrigerant</label><select id="rm-ref">${opts}</select></div>
      <div class="row"><label>Charge m (kg)</label><input id="rm-m" type="number" value="2.5" step="0.1" /></div>
      <div class="row"><label>Install h (m)</label><input id="rm-h" type="number" value="1.8" step="0.1" /></div>
      <div class="metric"><div class="metric-l">Estimated min floor area</div><div class="metric-v" id="rm-out">—</div><div class="metric-s" id="rm-formula">—</div></div>
      <div class="warn">Planning estimate only. Actual minimum depends on installation type, ventilation, mitigation features and the manufacturer's calculation per AS/NZS 60335.2.40.</div>
    `;
    const upd = () => {
      const k = document.getElementById('rm-ref').value;
      const m = parseFloat(document.getElementById('rm-m').value) || 0;
      const h = parseFloat(document.getElementById('rm-h').value) || 1.8;
      const r = REFRIGERANTS[k];
      const lfl_kg_m3 = r.lfl_gm3 / 1000;
      const A_min = Math.pow(m / (2.5 * Math.pow(lfl_kg_m3, 1.25) * h), 2);
      document.getElementById('rm-out').textContent = A_min.toFixed(1) + ' m²';
      document.getElementById('rm-formula').textContent = `LFL ${lfl_kg_m3.toFixed(3)} kg/m³, h ${h} m`;
    };
    document.getElementById('rm-ref').onchange = upd;
    document.getElementById('rm-m').oninput = upd;
    document.getElementById('rm-h').oninput = upd;
    upd();
  } else if (currentTool === 'masstemp') {
    const opts = Object.keys(REFRIGERANTS).filter(k => REFRIGERANTS[k].density57).map(k => `<option value="${k}">${k}</option>`).join('');
    body.innerHTML = `
      <div class="note" style="margin-top:0;">Temperature-corrected fill mass. AS 2030.5 sets fill ratio at 57 °C bulk-liquid; this estimates safe charge at actual liquid temperature.</div>
      <div class="row"><label>Refrigerant</label><select id="mt-ref">${opts}</select></div>
      <div class="row"><label>Water cap. (L)</label><input id="mt-wc" type="number" value="13.6" step="0.1" /></div>
      <div class="row"><label>Liquid T (°C)</label><input id="mt-t" type="number" value="20" step="1" /></div>
      <div class="row"><label>Use case</label><select id="mt-mode"><option value="new">New (3% ullage)</option><option value="rec">Recovered (20%)</option></select></div>
      <div class="metric"><div class="metric-l">Maximum charge</div><div class="metric-v" id="mt-out">—</div><div class="metric-s" id="mt-form">—</div></div>
      <div class="warn">Always check the cylinder's stamped maximum gross weight. Density values are approximations — refer to NIST REFPROP for precise data.</div>
    `;
    const upd = () => {
      const k = document.getElementById('mt-ref').value;
      const wc = parseFloat(document.getElementById('mt-wc').value) || 0;
      const t = parseFloat(document.getElementById('mt-t').value);
      const mode = document.getElementById('mt-mode').value;
      const r = REFRIGERANTS[k];
      const dT = r.density57 * (1 + 0.0035 * (57 - t));
      const ullage = mode === 'new' ? 0.97 : 0.80;
      const mass = ullage * dT * wc;
      document.getElementById('mt-out').textContent = mass.toFixed(2) + ' kg';
      document.getElementById('mt-form').textContent = `ρ@${t}°C ≈ ${dT.toFixed(3)} kg/L`;
    };
    document.getElementById('mt-ref').onchange = upd;
    document.getElementById('mt-wc').oninput = upd;
    document.getElementById('mt-t').oninput = upd;
    document.getElementById('mt-mode').onchange = upd;
    upd();
  } else if (currentTool === 'tco2') {
    const opts = Object.keys(REFRIGERANTS).filter(k => REFRIGERANTS[k].scheduled).map(k => `<option value="${k}">${k}</option>`).join('');
    body.innerHTML = `
      <div class="row"><label>Refrigerant</label><select id="tc-ref">${opts}</select></div>
      <div class="row"><label>Charge (kg)</label><input id="tc-kg" type="number" value="50" step="1" /></div>
      <div class="metric"><div class="metric-l">CO₂-equivalent</div><div class="metric-v" id="tc-out">—</div><div class="metric-s" id="tc-form">—</div></div>
      <div id="tc-tier"></div>
      <div class="note">Used for EU F-Gas leak inspection tiers and sustainability reporting. Switch jurisdiction at top to compare AR4 vs AR5 GWP.</div>
    `;
    const upd = () => {
      const k = document.getElementById('tc-ref').value;
      const kg = parseFloat(document.getElementById('tc-kg').value) || 0;
      const r = REFRIGERANTS[k];
      const gwp = jurisdiction === 'AU' ? r.gwp_au : r.gwp_nz;
      const tco2 = (kg * gwp) / 1000;
      document.getElementById('tc-out').textContent = tco2.toFixed(2) + ' tCO₂e';
      document.getElementById('tc-form').textContent = `${kg} kg × GWP ${gwp} (${jurisdiction === 'AU' ? 'AR4' : 'AR5'})`;
      let tier = '';
      if (tco2 < 5) tier = 'Below 5 — no F-Gas inspection tier';
      else if (tco2 < 50) tier = 'Tier 1 — 12 months (24 with detection)';
      else if (tco2 < 500) tier = 'Tier 2 — 6 months (12 with detection)';
      else tier = 'Tier 3 — 3 months (6 with detection)';
      document.getElementById('tc-tier').innerHTML = `<div class="ok">${tier}</div>`;
    };
    document.getElementById('tc-ref').onchange = upd;
    document.getElementById('tc-kg').oninput = upd;
    upd();
  }
}

const procSelect = document.getElementById('proc-select');
function renderProc() {
  const p = PROCEDURES[procSelect.value];
  let html = `
    <div style="margin-bottom: 12px;">
      <div style="font-size: 16px; font-weight: 500;">${p.title}</div>
      <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.4; margin-top: 2px;">${p.sub}</div>
    </div>
    <div class="card">
  `;
  p.steps.forEach((s, i) => { html += `<div class="step"><div class="step-n">${i + 1}</div><div>${s}</div></div>`; });
  html += '</div>';
  if (p.warn) html += `<div class="warn">${p.warn}</div>`;
  if (p.note) html += `<div class="note">${p.note}</div>`;
  html += `
    <div class="export-row">
      <button class="btn" id="exp-copy">Copy checklist</button>
      <button class="btn" id="exp-share">Share</button>
    </div>
  `;
  document.getElementById('proc-body').innerHTML = html;
  const buildText = () => {
    const date = new Date().toISOString().slice(0, 10);
    let txt = p.title.toUpperCase() + '\n' + p.sub + '\n\n';
    txt += 'Date: ' + date + '\nTechnician: ____________________\nLicence #: ____________________\nSite: ____________________\nRefrigerant: ____________________\nCharge: ________ kg\n\n';
    p.steps.forEach((s, i) => { txt += '[ ] ' + (i+1) + '. ' + s + '\n'; });
    if (p.warn) txt += '\nWARNING: ' + p.warn + '\n';
    if (p.note) txt += '\nNote: ' + p.note + '\n';
    txt += '\nSignature: ____________________\nDate completed: ____________________\n';
    return txt;
  };
  document.getElementById('exp-copy').onclick = () => {
    navigator.clipboard.writeText(buildText()).then(() => {
      const btn = document.getElementById('exp-copy');
      const orig = btn.textContent;
      btn.textContent = 'Copied ✓';
      setTimeout(() => { btn.textContent = orig; }, 1500);
    });
  };
  document.getElementById('exp-share').onclick = () => {
    if (navigator.share) {
      navigator.share({ title: p.title, text: buildText() }).catch(() => {});
    } else {
      navigator.clipboard.writeText(buildText());
      const btn = document.getElementById('exp-share');
      const orig = btn.textContent;
      btn.textContent = 'Copied ✓';
      setTimeout(() => { btn.textContent = orig; }, 1500);
    }
  };
}
procSelect.onchange = renderProc;

function renderInfo() {
  const k = document.getElementById('info-select').value;
  const i = INFO[k];
  let body = i.body || (jurisdiction === 'AU' ? i.body_au : i.body_nz);
  document.getElementById('info-body').innerHTML = `
    <div style="margin-bottom: 8px;"><div style="font-size: 15px; font-weight: 500;">${i.title}</div></div>
    <div class="card">${body}</div>
    <div class="src">${i.src}</div>
  `;
}
document.getElementById('info-select').onchange = renderInfo;

setJurisdiction(jurisdiction);
renderRefDetail();
renderCalc();
renderTool();
renderProc();
renderInfo();
