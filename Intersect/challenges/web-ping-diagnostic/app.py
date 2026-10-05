"""
Web Challenge: NetPulse Diagnostic Utility (Command Injection)
Bypass host verification or chain commands to read the FLAG environment variable.
"""
import os
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{missing_flag_env_var}")

# Ensure environment contains FLAG
os.environ["FLAG"] = FLAG

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>NetPulse // Server Diagnostics</title>
  <style>
    body { background: #0b0d13; color: #cbd5e1; font-family: 'JetBrains Mono', Consolas, monospace; padding: 40px 20px; margin: 0; }
    .container { max-width: 680px; margin: 0 auto; background: #131822; border: 1px solid #243044; border-radius: 8px; padding: 28px; box-shadow: 0 8px 30px rgba(0,0,0,0.5); }
    h1 { color: #38bdf8; font-size: 20px; margin-top: 0; display: flex; align-items: center; gap: 10px; }
    .badge { font-size: 11px; background: #0284c733; color: #38bdf8; border: 1px solid #0284c766; padding: 2px 8px; border-radius: 4px; }
    p { color: #94a3b8; font-size: 14px; }
    .form-group { margin: 20px 0; }
    label { display: block; font-size: 13px; color: #e2e8f0; margin-bottom: 8px; }
    .input-row { display: flex; gap: 8px; }
    input[type=text] { flex: 1; background: #0b0f17; border: 1px solid #334155; color: #f8fafc; padding: 10px 14px; border-radius: 4px; font-family: inherit; font-size: 14px; }
    input[type=text]:focus { outline: none; border-color: #38bdf8; }
    button { background: #0284c7; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; font-weight: 600; cursor: pointer; font-family: inherit; }
    button:hover { background: #0369a1; }
    .terminal { background: #07090e; border: 1px solid #1e293b; border-radius: 6px; padding: 16px; margin-top: 20px; font-size: 13px; color: #10b981; overflow-x: auto; white-space: pre-wrap; line-height: 1.5; }
    .terminal .header { color: #64748b; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 6px; font-size: 11px; }
  </style>
</head>
<body>
  <div class="container">
    <h1><span>⚡ NetPulse Host Diagnostic</span> <span class="badge">SEC-LEVEL-1</span></h1>
    <p>Perform live ICMP ping latency checks on internal network nodes.</p>
    
    <form method="POST">
      <div class="form-group">
        <label for="host">Target IP / Hostname:</label>
        <div class="input-row">
          <input type="text" id="host" name="host" placeholder="127.0.0.1" value="{{ target_host }}" required autocomplete="off">
          <button type="submit">Ping Host</button>
        </div>
      </div>
    </form>

    {% if output is not none %}
    <div class="terminal">
      <div class="header">SYS-EXEC EXECUTION STREAM:</div>
{{ output }}
    </div>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def ping():
    output = None
    target_host = ""
    if request.method == "POST":
        target_host = request.form.get("host", "").strip()
        if target_host:
            # Flawed filter: only blocks basic 'cat ' string, leaving command chaining open
            cmd = f"ping -n 1 {target_host}" if os.name == "nt" else f"ping -c 1 {target_host}"
            try:
                raw_out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
                output = raw_out.decode("utf-8", errors="replace")
            except subprocess.CalledProcessError as e:
                output = e.output.decode("utf-8", errors="replace") if e.output else str(e)
            except subprocess.TimeoutExpired:
                output = "Error: Diagnostic command timed out (5s limit)."
            except Exception as ex:
                output = f"Execution error: {str(ex)}"

    return render_template_string(PAGE, target_host=target_host, output=output)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
