from flask import Flask, request, jsonify, render_template_string
from predict import classify
import re

app = Flask(__name__)

# Enhanced single-file UI using Bootstrap and minimal JS. Replace your existing app.py with this file
# or save it as app_improved_ui.py and run `python app_improved_ui.py`.

HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Expense Analyzer — Demo</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(180deg,#f8fafc 0%, #eef2ff 100%); }
    .card { border-radius: 16px; box-shadow: 0 8px 24px rgba(39,39,54,0.08); }
    textarea { resize: vertical; }
    .monospace { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace; }
    .badge-cat { font-weight:600 }
  </style>
</head>
<body>
<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-lg-10">
      <div class="card p-4 mb-4">
        <div class="d-flex align-items-center mb-3">
          <div class="me-3">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L3 6v6c0 5 3.58 9.74 9 10 5.42-.26 9-5 9-10V6l-9-4z" fill="#6c5ce7" opacity=".12"/><path d="M12 2l9 4v6c0 5-3.58 9.74-9 10-5.42-.26-9-5-9-10V6l9-4z" stroke="#6c5ce7" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
          </div>
          <div>
            <h3 class="mb-0">AI Expense Analyzer</h3>
            <small class="text-muted">Paste bank/SMS transaction lines below — one per line. Click <strong>Analyze</strong>.</small>
          </div>
        </div>

        <div class="mb-3">
          <label for="smsInput" class="form-label">Transaction lines (paste here)</label>
          <textarea id="smsInput" rows="8" class="form-control monospace" placeholder="Your a/c XXXX debited by Rs 1299.50 at Zomato on 25-11-2025"></textarea>
        </div>

        <div class="d-flex gap-2">
          <button id="analyzeBtn" class="btn btn-primary">Analyze</button>
          <button id="clearBtn" class="btn btn-outline-secondary">Clear</button>
          <button id="exampleBtn" class="btn btn-outline-info">Load Example</button>
          <div class="ms-auto text-muted align-self-center" id="statusSmall"></div>
        </div>
      </div>

      <div id="resultsArea" style="display:none">
        <div class="row g-3">
          <div class="col-md-8">
            <div class="card p-3">
              <h5 class="mb-3">Parsed Transactions</h5>
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead class="table-light">
                    <tr><th>Text</th><th>Category</th><th>Amount</th></tr>
                  </thead>
                  <tbody id="txTableBody"></tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card p-3">
              <h5>Summary</h5>
              <div id="summaryList" class="mt-2"></div>
              <hr>
              <div>
                <button id="exportCsv" class="btn btn-sm btn-outline-primary">Export CSV</button>
                <button id="reAnalyze" class="btn btn-sm btn-outline-secondary">Re-run</button>
              </div>
            </div>

            <div class="card p-3 mt-3">
              <h6>Tips</h6>
              <ul class="small mb-0">
                <li>Use clear SMS lines for best results.</li>
                <li>Add merchant keywords (Zomato, Amazon, BPCL) to improve rules.</li>
                <li>To add OCR support later — integrate Tesseract and send extracted text here.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div id="emptyHint" class="text-center text-muted mt-4">
        <small>Tip: paste sample lines and click <strong>Analyze</strong> to see a live demo.</small>
      </div>

    </div>
  </div>
</div>

<script>
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const exampleBtn = document.getElementById('exampleBtn');
const smsInput = document.getElementById('smsInput');
const statusSmall = document.getElementById('statusSmall');
const resultsArea = document.getElementById('resultsArea');
const txTableBody = document.getElementById('txTableBody');
const summaryList = document.getElementById('summaryList');
const emptyHint = document.getElementById('emptyHint');
const exportCsv = document.getElementById('exportCsv');

exampleBtn.addEventListener('click', ()=>{
  smsInput.value = `Your a/c XXXX debited by Rs 1299.50 at Zomato on 25-11-2025.\nINR 499 paid to Netflix subscription on 01/11/2025.\nDebited ₹560 at Indian Oil pump\nPayment of Rs. 2899 to Flipkart order\nINR 150 paid to Ola Cabs for ride`;
});

clearBtn.addEventListener('click', ()=>{ smsInput.value=''; resultsArea.style.display='none'; emptyHint.style.display='block'; });

function formatAmount(a){ return a? ('₹'+Number(a).toFixed(2)) : '-' }

analyzeBtn.addEventListener('click', async ()=>{
  const text = smsInput.value.trim();
  if(!text){ alert('Paste some transaction lines first.'); return; }
  statusSmall.textContent = 'Analyzing...';
  analyzeBtn.disabled = true;
  try{
    const resp = await fetch('/classify',{
      method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({lines:text.split('\n')})
    });
    const data = await resp.json();
    // populate table
    txTableBody.innerHTML = '';
    for(const r of data.rows){
      const tr = document.createElement('tr');
      const tdText = document.createElement('td'); tdText.textContent = r.text;
      const tdCat = document.createElement('td'); tdCat.innerHTML = `<span class='badge bg-light text-dark badge-cat'>${r.category}</span>`;
      const tdAmt = document.createElement('td'); tdAmt.textContent = formatAmount(r.amount);
      tr.appendChild(tdText); tr.appendChild(tdCat); tr.appendChild(tdAmt);
      txTableBody.appendChild(tr);
    }
    // summary
    summaryList.innerHTML = '';
    const totals = data.totals;
    for(const k of Object.keys(totals)){
      const item = document.createElement('div'); item.className='d-flex justify-content-between';
      item.innerHTML = `<div>${k}</div><div><strong>₹${Number(totals[k]).toFixed(2)}</strong></div>`;
      summaryList.appendChild(item);
    }
    resultsArea.style.display='block'; emptyHint.style.display='none';
  }catch(e){
    alert('Error analyzing — see console.'); console.error(e);
  }finally{
    statusSmall.textContent = '';
    analyzeBtn.disabled = false;
  }
});

exportCsv.addEventListener('click', ()=>{
  const rows = Array.from(txTableBody.querySelectorAll('tr')).map(tr=>{
    const t = tr.children[0].textContent.replace(/"/g,'""');
    const c = tr.children[1].textContent.trim();
    const a = tr.children[2].textContent.trim().replace('₹','');
    return `"${t}","${c}","${a}"`;
  });
  if(rows.length===0){ alert('No data to export'); return; }
  const csv = 'text,category,amount\n' + rows.join('\n');
  const blob = new Blob([csv], {type:'text/csv'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'transactions.csv'; a.click(); URL.revokeObjectURL(url);
});

// allow Enter+Ctrl to analyze quickly
smsInput.addEventListener('keydown', (e)=>{ if(e.ctrlKey && e.key==='Enter'){ analyzeBtn.click(); } });

</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Server endpoints: / (serves UI) and /classify (JSON API)

AMOUNT_RE = re.compile(r'(?:Rs|INR|₹)\s?([0-9,]+(?:\.[0-9]{1,2})?)', re.I)

def extract_amount(text):
    m = AMOUNT_RE.search(text)
    if m:
        try:
            return float(m.group(1).replace(',',''))
        except:
            return 0.0
    return 0.0

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/classify', methods=['POST'])
def classify_api():
    data = request.get_json() or {}
    lines = data.get('lines', [])
    rows = []
    totals = {}
    for line in lines:
        text = line.strip()
        if not text:
            continue
        cat = classify(text)
        amt = extract_amount(text)
        rows.append({'text': text, 'category': cat, 'amount': amt})
        totals[cat] = round(totals.get(cat, 0.0) + amt, 2)
    # ensure all categories exist for display
    ordered_totals = dict(sorted(totals.items(), key=lambda x: -x[1]))
    return jsonify({'rows': rows, 'totals': ordered_totals})

if __name__ == '__main__':
    app.run(debug=True)
