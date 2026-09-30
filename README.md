# Sectumsempra v1.0

**Sectumsempra** is a fast automated attack execution and post exploitation framework engineered for CTFs, labs and authorized assessments.

### IMPORTANT: Use NetWeave first to map the target and find the attack vector, then launch Sectumsempra to slash through and capture the flags.

Turn a correlated attack path into active reverse shells and a ready privilege escalation pipeline.

TARGET
  │
  ▼
ATTACK PATH
  │
  ▼
FOOTHOLD PAYLOAD
  │
  ▼
REVERSE SHELL
  │
  ▼
PRIVILEGE ESCALATION

Sectumsempra ingests target parameters, automatically maps active local routing interfaces, builds tailored multi platform exploit vectors and stages immediate post exploitation discovery scripts.

## Deployment

### 1. Clone Sectumsempra

git clone https://github.com/danielissaq/Sectumsempra.git
cd Sectumsempra

### 2. Set up Python

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install netifaces

### 3. Verify Attack Interface

Sectumsempra automatically tracks local network topology to bind your listening interface. Ensure your TryHackMe VPN tunnel is active:

ip a show tun0

## Complete Attack Workflow

### 1. Scout with NetWeave

Launch your reconnaissance framework against the remote host:

python pwn_recon.py

Locate the optimal entry point provided under the GOLDEN PATH analysis output.

### 2. Launch Sectumsempra

Run the attack script to frame your exploitation assets:

python3 sectumsempra.py

Input the target IP address and specify your local listener port when prompted.

### 3. Start Listener

Open a separate terminal window or tab in Kali Linux and host the receiver socket:

nc -lvnp 4444

### 4. Deploy Asset

Execute the generated command sequence against the vulnerability vector exposed during the scouting phase.

### 5. Execute Privilege Escalation

Once the active connection drops back into your netcat listener terminal window enter the staged network link string to immediately push the PEAS discovery utility onto the target file system and grab root context.

## Generated Payload

After parameters are processed Sectumsempra compiles custom raw execution scripts in your local working directory:

sectum_linux_strike_<target>.sh
sectum_win_strike_<target>.ps1

## Requirements

Python 3.10+
netifaces library
Netcat listener backend

## Legal Notice

Sectumsempra is intended for CTFs, security research, authorized assessments and isolated laboratory environments.

Only use Sectumsempra against systems you own or have explicit permission to test.
