# Sectumsempra v1.0

**Sectumsempra** is an automated attack execution and post-exploitation framework for CTFs, labs, and authorized assessments, designed to follow the NetWeave workflow.

```text
TARGET ──► ATTACK PATH ──► FOOTHOLD PAYLOAD ──► REVERSE SHELL ──► PRIVILEGE ESCALATION
```

## Deployment

### 1. Clone & Setup
```bash
git clone https://github.com
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
Verifies network topology and `tun0`:
```bash
ip a show tun0
```

## Complete Attack Workflow

1. **Scout with NetWeave:** Run reconnaissance in your primary terminal:
```bash
python pwn_recon.py
```

2. **Launch Sectumsempra:** Open a separate terminal and execute:
```bash
cd ~/Sectumsempra
source .venv/bin/activate
python3 sectumsempra.py
```

3. **Start Listener:** Open a third terminal to start netcat:
```bash
nc -lvnp 4444
```

4. **Deploy Asset & Escalate:** Execute payload and push post-exploitation scripts.

## Generated Payload
Generates scripts such as `sectum_linux_strike_<target>.sh` and `sectum_win_strike_<target>.ps1`.

## Requirements
```text
Python 3.10+
netifaces
Netcat listener backend
```

## Legal Notice
For authorized assessments and labs only against systems you have permission to test.
