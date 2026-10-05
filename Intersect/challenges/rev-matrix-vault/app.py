"""
Reverse Engineering Challenge: Matrix Biometric Gatekeeper
Analyze the client-side authorization routine or reverse the checksum algorithm to recover the master code.
"""
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{missing_flag_env_var}")

# Target master passcode
MASTER_KEY = "NEXUS-9821-OMEGA"

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Biometric Gatekeeper // Access Core</title>
  <style>
    body { background: #07090e; color: #cbd5e1; font-family: 'JetBrains Mono', Consolas, monospace; padding: 40px 20px; }
    .card { max-width: 600px; margin: 0 auto; background: #0d1117; border: 1px solid #21262d; border-radius: 8px; padding: 30px; box-shadow: 0 10px 35px rgba(0,0,0,0.6); }
    h1 { color: #a855f7; font-size: 20px; margin-top: 0; }
    .badge { font-size: 11px; background: #a855f722; color: #c084fc; border: 1px solid #a855f766; padding: 2px 8px; border-radius: 4px; }
    p { color: #94a3b8; font-size: 13px; }
    .key-form { margin-top: 20px; }
    input[type=text] { width: 100%; box-sizing: border-box; background: #080b10; border: 1px solid #30363d; color: #f0f6fc; padding: 12px 14px; border-radius: 4px; font-family: inherit; font-size: 15px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; }
    input[type=text]:focus { outline: none; border-color: #a855f7; }
    button { width: 100%; background: #9333ea; color: #fff; border: none; padding: 12px; border-radius: 4px; font-weight: 700; font-family: inherit; cursor: pointer; font-size: 14px; }
    button:hover { background: #7e22ce; }
    .result { margin-top: 20px; padding: 14px; border-radius: 4px; font-size: 14px; }
    .success { background: #10b98122; border: 1px solid #10b981; color: #34d399; }
    .failure { background: #ef444422; border: 1px solid #ef4444; color: #f87171; }
    .code-box { background: #05070a; border: 1px solid #161b22; padding: 12px; border-radius: 4px; font-size: 11px; color: #6e7681; margin-top: 20px; overflow-x: auto; }
  </style>
</head>
<body>
  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h1>Matrix Gatekeeper</h1>
      <span class="badge">FIRMWARE v4.12</span>
    </div>
    <p>Enter the master cryptographic authorization key sequence to disengage the airlock lockouts.</p>

    <form method="POST" class="key-form" id="vault-form">
      <input type="text" name="key" id="key" placeholder="FORMAT: XXXX-0000-XXXX" required autocomplete="off">
      <button type="submit">Verify Master Key</button>
    </form>

    {% if message %}
      <div class="result {{ 'success' if unlocked else 'failure' }}">
        {{ message }}
      </div>
    {% endif %}

    <div class="code-box">
      <div>// FIRMWARE VERIFICATION LOGIC DISASSEMBLY:</div>
      <div id="firmware-src">
        /*
          const _chk = (k) => {
            const parts = k.split('-');
            if(parts.length !== 3) return false;
            const p1 = parts[0].split('').reduce((a,c) => a + c.charCodeAt(0), 0);
            const p2 = parseInt(parts[1], 10);
            const p3 = parts[2].split('').reverse().join('');
            return (p1 === 390 && p2 === 9821 && p3 === "AGEMO");
          };
        */
      </div>
    </div>
  </div>

  <script>
    // Client-side quick validator (inspectable)
    function validateKey(input) {
      const parts = input.toUpperCase().trim().split('-');
      if (parts.length !== 3) return false;
      const p1_sum = parts[0].split('').reduce((a, c) => a + c.charCodeAt(0), 0);
      const p2_val = parseInt(parts[1], 10);
      const p3_rev = parts[2].split('').reverse().join('');
      return (p1_sum === 390 && p2_val === 9821 && p3_rev === "AGEMO");
    }
  </script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def gatekeeper():
    message = None
    unlocked = False
    if request.method == "POST":
        submitted_key = request.form.get("key", "").strip().upper()
        if submitted_key == MASTER_KEY:
            message = f"ACCESS GRANTED // AIRLOCK OPEN! Flag: {FLAG}"
            unlocked = True
        else:
            message = "ACCESS DENIED // INVALID AUTHORIZATION KEY SEQUENCE."

    return render_template_string(PAGE, message=message, unlocked=unlocked)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
