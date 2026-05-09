# NetworkCap1 — Chrome Update Malware Download

- **Purpose:** This challenge simulates a compromised host downloading a malicious executable disguised as a Chrome browser update from a suspicious external server.

- **How to Solve:** Open the PCAP in Wireshark, filter for `ip.addr == 185.62.14.33`, follow the TCP stream, and locate the MZ/DOS header in the HTTP response body — immediately following the DOS stub you will find a Base64 encoded string.

- **Flag:** Decode the Base64 string to retrieve the flag: `hcr{FrameContainsDOSMode}`

---

**Encoded Flag:**
```
aGNye0ZyYW1lQ29udGFpbnNET1NNb2RlfQ==
```

**Wireshark Filter:**
```
ip.addr == 185.62.14.33
```
