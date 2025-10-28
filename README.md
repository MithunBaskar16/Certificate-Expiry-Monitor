# 🔐 Certificate Expiry Monitor (AI Agent)

An **AI-based SSL/TLS Certificate Monitoring System** that automatically checks website certificate expiry dates, stores results in a database, and displays them on a **Flask web dashboard** with alerting capabilities.

---

## 🚀 Overview

The **Certificate Expiry Monitor** helps DevOps and IT Security teams prevent website or API downtime caused by expired SSL/TLS certificates.

- 🕒 Automatically checks expiry dates for multiple domains  
- 💾 Stores results in a local SQLite database  
- 🌐 Displays status on a Flask web dashboard  
- 📧 Sends alerts before expiry (email/Telegram supported in next stage)  
- 🤖 Designed with future AI-enhanced prediction in mind  

---

## 🧠 How It Works

1. The script connects securely to each listed domain using Python’s `ssl` and `socket` libraries.  
2. It retrieves the certificate’s **expiry date (notAfter)**.  
3. The system calculates how many days are left until expiry.  
4. Results are stored in a SQLite database (`certs.db`).  
5. A Flask web app displays expiry data in a color-coded dashboard:
   - 🟢 **Safe** (> 30 days)
   - 🟡 **Warning** (10–30 days)
   - 🔴 **Critical** (< 10 days)

---

## 🧩 Architecture

