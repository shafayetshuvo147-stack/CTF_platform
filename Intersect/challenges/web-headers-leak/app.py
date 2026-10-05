"""
Web Challenge: Undercover API
Inspect response headers, robot definitions, and internal debug routes.
"""
import os
from flask import Flask, Response, jsonify, render_template_string

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{missing_flag_env_var}")

PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Corporate Staging Portal</title>
  <style>
    body { background: #0e1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 50px; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 30px; max-width: 600px; margin: 0 auto; }
    h1 { color: #58a6ff; }
    .badge { background: #ff7b7233; color: #ff7b72; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    code { background: #21262d; padding: 2px 6px; border-radius: 4px; color: #7ee787; }
  </style>
</head>
<body>
  <div class="card">
    <span class="badge">STAGING ENVIRONMENT</span>
    <h1>Corporate Undercover Portal</h1>
    <p>This service is strictly for internal QA testing. All external traffic is logged and monitored.</p>
    <p>Debug mode status: <code>ACTIVE</code></p>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    resp = Response(render_template_string(PAGE), mimetype="text/html")
    resp.headers["X-Backend-Server"] = "Nexus-Internal-GW/2.4.1"
    resp.headers["X-Internal-Secret-Route"] = "/api/v2/diagnostics/dump"
    return resp


@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /api/v2/diagnostics/dump\n", mimetype="text/plain")


@app.route("/api/v2/diagnostics/dump")
def debug_dump():
    return jsonify({
        "status": "ok",
        "debug_log": [
            "Initializing secure keystore...",
            "Loading cryptographic tokens...",
            f"Flag injected: {FLAG}",
        ],
        "environment": "staging",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
