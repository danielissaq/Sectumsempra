# Sectumsempra v1.0

**Sectumsempra** is an automated attack execution and post-exploitation framework for CTFs, labs, and authorized assessments, designed to follow the NetWeave workflow.

```text
TARGET ──► ATTACK PATH ──► FOOTHOLD PAYLOAD ──► REVERSE SHELL ──► PRIVILEGE ESCALATION
```

## Deployment

### 1. Clone Sectumsempra
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
Ensure your VPN tunnel is active:
```bash
ip a show tun0
```

## Complete Attack Workflow

1. **Scout with NetWeave:** Run `python pwn_recon.py` to find the entry point.
2. **Launch Sectumsempra:** Run `python3 sectumsempra.py` and provide the target IP and listener port.
3. **Start Listener:** Run `nc -lvnp 4444` in a separate terminal.
4. **Deploy Asset & Escalate:** Execute the generated exploit and push post-exploitation scripts for root access.

## Generated Payload
Generates scripts such as `sectum_linux_strike_<target>.sh` and `sectum_win_strike_<target>.ps1`.

## Requirements
Python 3.10+, `netifaces`, and a netcat listener.

## Legal Notice
For authorized assessments and labs only against systems you have permission to test.
