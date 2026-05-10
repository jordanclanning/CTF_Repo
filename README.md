# CTF_Repo

A collection of Capture The Flag (CTF) challenges organized by category. Designed for security training, skill development, and competition practice. Challenges range from beginner to intermediate and cover web exploitation, reverse engineering, and network forensics.

---

## Structure

```
CTF_Repo/
├── Forensics/
│   └── Web/                  # PCAP-based network forensics challenges
│       └── May2026/
├── Reverse_Engineering/
│   ├── Linux/                  # Linux binary challenges
│   │   └── May2026/
│   └── Windows/                   # Windows binary challenges (coming soon)
└── Web/                      # Web exploitation challenges
    ├── April2026/
    └── May2026/
```

---

## Categories

### Forensics
Network and file-based forensics challenges. Analyze packet captures to uncover suspicious activity and recover hidden flags.
- Tools: Wireshark, tshark, CyberChef
- [Go to Forensics](./Forensics/)

---

### Reverse Engineering
Linux ELF and Windows PE binary challenges. Use debuggers and decompilers to analyze binaries and extract flags.
- Tools: GDB, Ghidra, x64dbg, strings
- [Go to Reverse Engineering](./Reverse_Engineering/)

---

### Web
Docker-based web exploitation challenges covering source inspection, client-side logic flaws, remote code execution, and SQL injection.
- Tools: Burp Suite, browser DevTools, sqlmap, curl
- [Go to Web](./Web/)

    ### NOTE - Web/April2026 challenges may need modification for file paths as the GitHub directory was cloned & modified.

---

## Usage

All challenges in this repo are free to use, deploy, and modify. Whether you are running a CTF event, training a team, or practicing on your own — pull the repo and get started. All challenges have been tested and verified to work as intended.

```bash
git clone https://github.com/jordanclanning/CTF_Repo.git
```

> **Note:** If you are hosting these challenges for others, rename files and folders as needed to avoid giving away context or challenge names before players attempt them. Flag values can also be swapped out to fit your event's flag format.

---

## Getting Started

### Web Challenges
```bash
cd Web/April2026
docker-compose up
# navigate to http://localhost:8080
```

### Reverse Engineering Challenges
```bash
cd Reverse_Engineering/ELF/May2026
# load binary in Ghidra or run under GDB
gdb ./challenge_binary
```

### Forensics Challenges
```bash
# open PCAP in Wireshark
wireshark Forensics/Web/May2026/HCR1.pcap
```

---

## Difficulty

| Challenge | Category | Difficulty | Date Added |
|---|---|---|---|
| Challenge1Lann | Web | Easy | April 2026 |
| Challenge2Lann | Web | Easy | April 2026 |
| Challenge3Lann | Web | Easy | April 2026 |
| Challenge4Lann | Web | Medium | April 2026 |
| Challenge5Lann | Web | Medium | April 2026 |
| Wheres_The_Flag | RE/Linux | Easy | April 2026 |
| challenge_split | RE/Linux | Easy | April 2026 |
| malicious_calculator | RE/Linux | Easy | April 2026 |
| ransomware | RE/Linux | Easy | April 2026 |
| HCR1.pcap | Forensics/Web | Easy | May 2026 |
