import ssl
import socket
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string

# ==========================
# 1. Database Setup
# ==========================
DB_FILE = "certs.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS certificates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE,
                    expiry_date TEXT,
                    days_left INTEGER,
                    last_checked TEXT
                )''')
    conn.commit()
    conn.close()

# ==========================
# 2. Certificate Checker
# ==========================
def get_expiry_date(hostname):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            return expiry_date

def update_database(domain_list):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    for domain in domain_list:
        try:
            expiry_date = get_expiry_date(domain)
            days_left = (expiry_date - datetime.utcnow()).days
            last_checked = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            c.execute('''INSERT OR REPLACE INTO certificates (id, domain, expiry_date, days_left, last_checked)
                         VALUES (
                             COALESCE((SELECT id FROM certificates WHERE domain=?), NULL),
                             ?, ?, ?, ?
                         )''', (domain, domain, expiry_date.strftime("%Y-%m-%d"), days_left, last_checked))
            print(f"[OK] {domain} → {days_left} days left")

        except Exception as e:
            print(f"[Error] {domain}: {e}")

    conn.commit()
    conn.close()

# ==========================
# 3. Flask Dashboard
# ==========================
app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SSL Certificate Monitor</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f4f4f4; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ccc; text-align: center; }
        th { background-color: #222; color: white; }
        .safe { background-color: #c8e6c9; }
        .warn { background-color: #fff9c4; }
        .danger { background-color: #ffcdd2; }
    </style>
</head>
<body>
    <h1>SSL Certificate Expiry Monitor</h1>
    <table>
        <tr>
            <th>Domain</th>
            <th>Expiry Date</th>
            <th>Days Left</th>
            <th>Last Checked</th>
        </tr>
        {% for row in data %}
        <tr class="{{ 'danger' if row[3] < 10 else 'warn' if row[3] < 30 else 'safe' }}">
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
            <td>{{ row[4] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM certificates ORDER BY days_left ASC")
    data = c.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, data=data)

# ==========================
# 4. Main
# ==========================
if __name__ == "__main__":
    init_db()
    domains = ["google.com", "github.com", "example.com"]
    update_database(domains)
    app.run(debug=True)
