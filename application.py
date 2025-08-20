from flask import Flask, request, jsonify, send_file
import io, zipfile, os

application = Flask(__name__)

# Tasas de ejemplo (fijas)
RATES = {
    "USD_EUR": 0.92,
    "EUR_USD": 1.09,
    "COP_USD": 0.00027,
    "USD_COP": 3700.0,
    "EUR_COP": 4040.0,   # ejemplos adicionales para pares
    "COP_EUR": 0.000247
}

def convert_amount(frm: str, to: str, amount: float):
    key = f"{frm}_{to}"
    if key not in RATES:
        return None, key
    rate = RATES[key]
    return amount * rate, rate

@application.route('/')
def index():
    return """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Conversor de Monedas</title>
  <style>
    :root {
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
      --bg: #f4f7fb;
      --card: #ffffff;
      --accent: #2563eb;
      --muted: #6b7280;
      --success: #10b981;
      --danger: #ef4444;
    }
    body { background: var(--bg); margin:0; padding:30px; color:#111827; }
    .container { max-width:760px; margin:0 auto; }
    .card { background:var(--card); border-radius:12px; padding:22px; box-shadow:0 6px 18px rgba(15,23,42,0.06); }
    h1 { margin:0 0 8px; font-size:22px; }
    p.lead { color:var(--muted); margin-top:0; }
    .row { display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-top:16px; }
    select, input[type="number"] { padding:10px 12px; border-radius:8px; border:1px solid #e5e7eb; font-size:14px; }
    button { background:var(--accent); color:white; border:none; padding:10px 14px; border-radius:8px; cursor:pointer; font-weight:600; }
    button.secondary { background:#fff; color:var(--accent); border:1px solid #dbeafe; }
    .result { margin-top:18px; padding:12px; border-radius:8px; background:#f8fafc; color:#063970; font-weight:700; }
    .note { margin-top:8px; color:var(--muted); font-size:13px; }
    .controls { margin-top:14px; display:flex; gap:10px; flex-wrap:wrap; }
    .inline { display:flex; gap:8px; align-items:center; }
    @media (max-width:520px){ .row { flex-direction:column; align-items:stretch; } .controls { flex-direction:column; } }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>Conversor de Moneda</h1>
      <p class="lead">Selecciona la moneda de origen y la moneda destino, ingresa el monto y presiona <strong>Convertir</strong>.</p>

      <div class="row">
        <div class="inline">
          <label for="from" style="margin-right:8px;">Desde</label>
          <select id="from">
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="COP">COP</option>
          </select>
        </div>

        <div class="inline">
          <label for="to" style="margin-right:8px;">Hacia</label>
          <select id="to">
            <option value="EUR">EUR</option>
            <option value="USD">USD</option>
            <option value="COP">COP</option>
          </select>
        </div>

        <div class="inline" style="flex:1;">
          <label for="amount" style="margin-right:8px;">Monto</label>
          <input id="amount" type="number" min="0" step="any" placeholder="ej: 100.00" value="1"/>
        </div>
      </div>

      <div class="controls">
        <button id="convertBtn">Convertir</button>
        <button id="downloadBtn" class="secondary" title="Descargar código">Descargar código (ZIP)</button>
      </div>

      <div id="output" class="result" style="display:none;"></div>
      <div id="error" class="result" style="display:none; background: #fff1f0; color: #7a1f1f;"></div>

    </div>
  </div>

  <script>
    const convertBtn = document.getElementById('convertBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const output = document.getElementById('output');
    const errorBox = document.getElementById('error');

    function showResult(text) {
      errorBox.style.display = 'none';
      output.style.display = 'block';
      output.innerText = text;
    }
    function showError(text) {
      output.style.display = 'none';
      errorBox.style.display = 'block';
      errorBox.innerText = text;
    }

    convertBtn.addEventListener('click', async () => {
      const frm = document.getElementById('from').value;
      const to = document.getElementById('to').value;
      const amount = document.getElementById('amount').value;

      if (!amount || Number(amount) < 0) {
        showError('Ingresar un monto válido (≥ 0).');
        return;
      }
      if (frm === to) {
        showError('Selecciona monedas diferentes para convertir.');
        return;
      }

      try {
        const params = new URLSearchParams({ from: frm, to: to, amount: amount });
        const res = await fetch('/api/convert?' + params.toString());
        const data = await res.json();
        if (!res.ok) {
          showError('Error: ' + (data.error || 'Par no soportado'));
          return;
        }
        const formatted = `${data.amount} ${data.from} = ${data.result} ${data.to} (tasa=${data.rate})`;
        showResult(formatted);
      } catch (e) {
        showError('Error de conexión: ' + e.message);
      }
    });

    downloadBtn.addEventListener('click', () => {
      // Hacer que el navegador descargue /download (botón en lugar de link)
      window.location.href = '/download';
    });
  </script>
</body>
</html>
    """

@application.route('/api/convert')
def api_convert():
    frm = request.args.get('from', '').upper()
    to = request.args.get('to', '').upper()
    try:
        amount = float(request.args.get('amount', '1'))
    except:
        return jsonify({"error": "amount debe ser número"}), 400

    result, rate = convert_amount(frm, to, amount)
    if result is None:
        return jsonify({"error": "Par no soportado", "supported_pairs": list(RATES.keys())}), 400

    return jsonify({
        "from": frm,
        "to": to,
        "amount": amount,
        "rate": rate,
        "result": round(result, 6)
    })

@application.route('/download')
def download_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        files = ['application.py', 'requirements.txt', 'README.md']
        for fname in files:
            if os.path.exists(fname):
                z.write(fname)
            else:
                z.writestr(fname, f"# {fname} - generado automáticamente\\n")
    buf.seek(0)
    return send_file(buf, mimetype='application/zip', as_attachment=True, download_name='mi_app_ec2.zip')

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True)


