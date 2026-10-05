"""
Crypto Challenge: Caesar Vault Service
Decrypt the ciphertext to discover the passcode and retrieve the flag!
"""
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{missing_flag_env_var}")
SECRET_CODE = "OPENSESAME"
SHIFT = 13


def rot13(text: str) -> str:
    result = []
    for char in text:
        if 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + SHIFT) % 26 + ord('A')))
        elif 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + SHIFT) % 26 + ord('a')))
        else:
            result.append(char)
    return "".join(result)


PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Ancient Vault Cipher</title>
  <style>
    body { background: #0c0f14; color: #d0d8e2; font-family: monospace; padding: 40px; }
    .box { background: #161c24; border: 1px solid #29384d; border-radius: 8px; padding: 24px; max-width: 500px; margin: 0 auto; }
    h2 { color: #00e5a3; margin-top: 0; }
    input[type=text] { background: #0d1218; border: 1px solid #33445c; color: #fff; padding: 8px 12px; width: 80%; margin: 8px 0; border-radius: 4px; font-family: monospace; }
    input[type=submit] { background: #00e5a3; color: #051410; border: none; padding: 8px 16px; font-weight: bold; border-radius: 4px; cursor: pointer; }
    .msg { margin-top: 16px; padding: 10px; border-radius: 4px; }
    .success { background: #00e5a322; border: 1px solid #00e5a3; color: #00e5a3; }
    .error { background: #ff475722; border: 1px solid #ff4757; color: #ff6b81; }
    .cipher { color: #fbc531; font-weight: bold; }
  </style>
</head>
<body>
  <div class="box">
    <h2>[VAULT ACCESS TERMINAL]</h2>
    <p>Intercepted encrypted transmission signal:</p>
    <p>Encrypted Passcode: <span class="cipher">{{ encrypted_secret }}</span></p>
    <hr style="border-color:#29384d">
    <form method="post">
      <label>Enter Decrypted Passphrase:</label><br>
      <input type="text" name="passcode" placeholder="ENTER CODE" autocomplete="off" required><br>
      <input type="submit" value="Unlock Vault">
    </form>
    {% if message %}
      <div class="msg {{ 'success' if success else 'error' }}">{{ message }}</div>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def vault():
    encrypted_secret = rot13(SECRET_CODE)
    message = None
    success = False

    if request.method == "POST":
        passcode = request.form.get("passcode", "").strip().upper()
        if passcode == SECRET_CODE:
            message = f"VAULT UNLOCKED! Flag: {FLAG}"
            success = True
        else:
            message = "ACCESS DENIED: Invalid passcode."

    return render_template_string(PAGE, encrypted_secret=encrypted_secret, message=message, success=success)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
