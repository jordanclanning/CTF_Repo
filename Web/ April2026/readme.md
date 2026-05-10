# Web — April 2026

Docker-based web exploitation challenges. Each challenge runs as a self-contained container. Spin up with the provided `docker-compose.yml` and start hacking.

```bash
docker-compose up
```

---

## Challenges

### Challenge1Lann
- **Purpose:** Gain familiarity with web browser developer tools.
- **How to Solve:** Inspect the page source.
- **Flag:** `Summit{HTML_Source_Always_Tells_The_Truth}`

---

### Challenge2Lann
- **Purpose:** Gain familiarity with web browser developer tools.
- **How to Solve:** Inspect the page source.
- **Flag:** `Summit{Client_Side_Logic_Is_Not_Security}`

---

### Challenge3Lann
- **Purpose:** Gain familiarity with web browser developer tools.
- **How to Solve:** Inspect the page source.
- **Flag:** `Summit{Passenger_Feedback_Exposed_Client_Side_Data}`

---

### Challenge4Lann
- **Purpose:** Attempt to exploit a Remote Code Execution vulnerability on the diagnostics terminal.
- **How to Solve:** Run a series of commands to identify possible security gaps.
- **Flag:** `Summit{Airport_Diagnostics_Allowed_Command_Execution}`

---

### Challenge5Lann
- **Purpose:** Demonstrate how SQL Injection vulnerabilities work.
- **How to Solve:** Use common SQL Injection techniques.
- **Flag:** `Summit{SQLInjectionsAreFun}`

---

## Recommended Tools
- **Burp Suite** — intercepting and manipulating HTTP traffic
- **browser DevTools** — inspecting page source, cookies, and requests
- **sqlmap** — automated SQL injection testing
- **curl** — quick HTTP requests from the command line
