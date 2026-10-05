"""
CTF Challenge: Linux SUID Binary Escalation [MISC]
Points: 175 pts | Difficulty: Easy
A custom binary on the server has the SUID permission bit set (chmod u+s). Exploit GTFOBins techniques to escalate from low-privilege user to root.
"""
import os
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{missing_flag_env_var}")

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Linux SUID Binary Escalation // CTF Challenge</title>
  <style>
    body { background: #0b0e14; color: #cbd5e1; font-family: 'JetBrains Mono', Consolas, monospace; padding: 40px 20px; margin: 0; }
    .card { max-width: 780px; margin: 0 auto; background: #131822; border: 1px solid #243044; border-radius: 8px; padding: 28px; box-shadow: 0 10px 35px rgba(0,0,0,0.5); }
    h1 { color: #38bdf8; font-size: 20px; margin-top: 0; display: flex; align-items: center; justify-content: space-between; }
    .badge { font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: bold; background: #0284c722; color: #38bdf8; border: 1px solid #0284c755; }
    .badge.cat { background: #8b5cf622; color: #a78bfa; border-color: #8b5cf655; }
    .badge.diff { background: #f59e0b22; color: #f59e0b; border-color: #f59e0b55; }
    .desc { color: #94a3b8; font-size: 13.5px; line-height: 1.6; margin: 16px 0; }
    .terminal { background: #080b10; border: 1px solid #1e293b; border-radius: 6px; padding: 16px; margin: 18px 0; font-size: 13px; color: #10b981; overflow-x: auto; }
    .terminal .header { color: #64748b; font-size: 11px; border-bottom: 1px solid #1e293b; padding-bottom: 6px; margin-bottom: 10px; }
    input[type=text], input[type=password] { width: 100%; box-sizing: border-box; background: #080b10; border: 1px solid #334155; color: #f8fafc; padding: 10px 14px; border-radius: 4px; font-family: inherit; font-size: 14px; margin-bottom: 12px; }
    button { background: #0284c7; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; font-weight: 600; cursor: pointer; font-family: inherit; }
    button:hover { background: #0369a1; }
    .hint-box { background: #161e2e; border-left: 3px solid #38bdf8; padding: 12px; margin-top: 20px; font-size: 12px; color: #94a3b8; }
  </style>
</head>
<body>
  <div class="card">
    <h1>
      <span>Linux SUID Binary Escalation</span>
      <div>
        <span class="badge cat">MISC</span>
        <span class="badge diff">Easy</span>
        <span class="badge">175 PTS</span>
      </div>
    </h1>
    <div class="desc">A custom binary on the server has the SUID permission bit set (chmod u+s). Exploit GTFOBins techniques to escalate from low-privilege user to root.</div>

    <div class="terminal">
      <div class="header">MISSION INTERCEPT & TARGET PARAMETERS</div>
      <div>[+] Target Module: misc-linux-suid-privesc</div>
      <div>[+] Challenge Category: misc</div>
      <div>[+] Isolated Session Active. Inspect target parameters to uncover vulnerability.</div>
      <div style="color:#38bdf8; margin-top:8px;">[+] Target System Online. Flag is injected into this instance.</div>
    </div>

    <form method="POST">
      <label style="font-size:13px; color:#e2e8f0; display:block; margin-bottom:6px;">Target Payload / Key Validation:</label>
      <input type="text" name="query" placeholder="Enter test payload or exploration string..." autocomplete="off">
      <button type="submit">Execute Test</button>
    </form>

    {% if result %}
    <div class="terminal" style="margin-top:16px; color:#f8fafc;">
      <div class="header">RESPONSE OUTPUT</div>
      <pre style="margin:0; font-family:inherit;">{{ result }}</pre>
    </div>
    {% endif %}

    <div class="hint-box">
      <strong>💡 FIELD OPERATOR TIP:</strong> SUID privilege escalation. Connect tools or intercept traffic to extract the flag.
    </div>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        q = request.form.get("query", "").strip()
        if q:
            result = f"Server processed input query: {q}\nStatus: 200 OK\nTarget environment variable FLAG loaded in memory."
    return render_template_string(PAGE, result=result)

@app.route("/api/flag")
def api_flag():
    return jsonify({"status": "ok", "challenge": "misc-linux-suid-privesc", "flag": FLAG})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
