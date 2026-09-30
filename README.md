# Sectumsempra v1.0

**Sectumsempra** is an automated attack execution and post-exploitation framework for CTFs, labs, and authorized assessments, designed to follow the NetWeave workflow.

```text
TARGET ──► ATTACK PATH ──► FOOTHOLD PAYLOAD ──► REVERSE SHELL ──► PRIVILEGE ESCALATION
```

## Deployment

### 1. Clone Sectumsempra
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
Ensure your VPN tunnel is active:
```bash
ip a show tun0
```

## Complete Attack Workflow

### Multi-Terminal Execution
For the optimal operational workflow, maintain your active NetWeave results screen in your primary terminal, and open a secondary terminal window or tab to manage execution.

### Execution Sequence

1. **Scout with NetWeave:** In your first terminal window, launch your reconnaissance core against the host to pinpoint the active exposure point under the GOLDEN PATH output:
```bash
python pwn_recon.py
```

2. **Launch Sectumsempra:** Open a second terminal window or tab, enter the project workspace, activate the environment, and initialize the payload compiler:
```bash
cd ~/Final_Automation_Test/Sectumsempra
source .venv/bin/activate
python3 sectumsempra.py
```
Input the targeted IP address and assign your designated incoming shell port when prompted.

3. **Start Listener:** In a separate listener terminal window or tab, initialize your netcat socket handler to receive the incoming connection loop:
```bash
nc -lvnp 4444
```

4. **Deploy Asset & Escalate:** Execute the tailored deployment payload against the target component exposed by NetWeave. Once the active terminal session drops back into your netcat listener, trigger the staged environment audit line to map out local paths.

## Generated Payload
Compiles standard functional execution vectors within your immediate working path:
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
For authorized assessments and labs only against systems you have permission to test.
