"""
Forensics Challenge: Operation Phantom Beacon
Log analysis portal containing realistic SIEM audit logs with an exfiltrated base64 flag payload.
"""
import os
import base64
from flask import Flask, Response, render_template_string, jsonify

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{missing_flag_env_var}")


def generate_logs(flag_str: str):
    b64_flag = base64.b64encode(flag_str.encode("utf-8")).decode("utf-8")
    
    logs = [
        {"ts": "2026-09-08 04:12:01", "src": "10.0.4.12", "type": "AUTH", "msg": "PAM session opened for user service-cron by (uid=0)"},
        {"ts": "2026-09-08 04:15:22", "src": "192.168.1.104", "type": "HTTP", "msg": "GET /api/v1/health status=200 size=42 agent='Mozilla/5.0'"},
        {"ts": "2026-09-08 04:22:18", "src": "172.16.88.5", "type": "FW", "msg": "DROP IN=eth0 OUT= SRC=203.0.113.44 DST=172.16.88.5 PROTO=TCP SPT=48212 DPT=22"},
        {"ts": "2026-09-08 04:31:05", "src": "10.0.4.12", "type": "AUDIT", "msg": "EXECVE comm='curl' arg0='curl' arg1='-s' arg2='https://telemetry-gateway.internal.net/sync'"},
        {"ts": "2026-09-08 04:33:49", "src": "10.0.4.99", "type": "HTTP", "msg": "POST /gateway/sync?session=anon&stage=init status=200 size=18"},
        {"ts": "2026-09-08 04:38:12", "src": "10.0.4.99", "type": "BEACON", "msg": f"DEBUG_OUT telemetry_chunk=0x4174 payload='{b64_flag}' egress_channel=shadow_dns"},
        {"ts": "2026-09-08 04:40:02", "src": "192.168.1.104", "type": "HTTP", "msg": "GET /api/v1/metrics status=200 size=1042 agent='Prometheus/2.45'"},
        {"ts": "2026-09-08 04:45:19", "src": "10.0.4.12", "type": "AUTH", "msg": "PAM session closed for user service-cron"},
        {"ts": "2026-09-08 04:50:00", "src": "127.0.0.1", "type": "SYS", "msg": "Logrotate routine completed on /var/log/audit.log"},
    ]
    return logs


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SOC SIEM // Security Incident Audit</title>
  <style>
    body { background: #080b10; color: #cbd5e1; font-family: 'JetBrains Mono', Consolas, monospace; padding: 40px 20px; margin: 0; }
    .container { max-width: 900px; margin: 0 auto; background: #0f141d; border: 1px solid #1e293b; border-radius: 8px; padding: 24px; }
    h1 { color: #f59e0b; font-size: 19px; margin-top: 0; display: flex; align-items: center; justify-content: space-between; }
    .status { font-size: 12px; background: #ef444422; color: #ef4444; border: 1px solid #ef444466; padding: 3px 8px; border-radius: 4px; }
    .desc { color: #94a3b8; font-size: 13px; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 15px; }
    th { text-align: left; background: #161f2e; color: #94a3b8; padding: 10px; border-bottom: 1px solid #334155; }
    td { padding: 10px; border-bottom: 1px solid #1e293b; color: #e2e8f0; }
    tr:hover { background: #151d2a; }
    .badge-type { padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 11px; }
    .type-BEACON { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b55; }
    .type-AUTH { background: #3b82f622; color: #60a5fa; }
    .type-HTTP { background: #10b98122; color: #34d399; }
    .type-FW { background: #ef444422; color: #f87171; }
    .type-AUDIT { background: #8b5cf622; color: #a78bfa; }
    .type-SYS { background: #64748b22; color: #94a3b8; }
    .raw-btn { display: inline-block; margin-top: 15px; background: #1e293b; color: #38bdf8; text-decoration: none; padding: 8px 14px; border-radius: 4px; font-size: 12px; border: 1px solid #334155; }
    .raw-btn:hover { background: #334155; }
  </style>
</head>
<body>
  <div class="container">
    <h1>
      <span>🚨 SIEM Access Audit Log — Incident #IR-8821</span>
      <span class="status">HIGH SEVERITY BREACH</span>
    </h1>
    <div class="desc">
      Incident description: An egress beacon was detected transmitting encoded memory snippets to an external staging sink. Inspect the audit stream to isolate the exfiltrated flag.
    </div>

    <table>
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Source IP</th>
          <th>Type</th>
          <th>Event Message</th>
        </tr>
      </thead>
      <tbody>
        {% for log in logs %}
        <tr>
          <td style="color:#64748b">{{ log.ts }}</td>
          <td style="color:#38bdf8">{{ log.src }}</td>
          <td><span class="badge-type type-{{ log.type }}">{{ log.type }}</span></td>
          <td style="word-break: break-all;">{{ log.msg }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <a href="/api/raw" class="raw-btn" target="_blank">View Raw Syslog Export ↗</a>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    logs = generate_logs(FLAG)
    return render_template_string(PAGE, logs=logs)


@app.route("/api/raw")
def raw_logs():
    logs = generate_logs(FLAG)
    raw_lines = [f"[{l['ts']}] [{l['type']}] [{l['src']}] {l['msg']}" for l in logs]
    return Response("\n".join(raw_lines), mimetype="text/plain")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
