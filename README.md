Sectumsempra v1.0

Sectumsempra is an automated attack script and payload framework engineered for CTF challenges. It takes target parameters and crafts multi platform scripts to capture reverse shells and handle privilege escalation.

Features
Maps local network routing to prioritize active VPN pipelines like tun0.
Compiles execution setups for Linux bash and Windows powershell files.
Pre stages download commands for automated local privilege escalation assessment tools.

Deployment
git clone https://github.com
cd Sectumsempra
python3 -m venv .venv
source .venv/bin/activate
pip install netifaces

Execution
python3 sectumsempra.py

Requirements
Python 3.10 plus
netifaces library
Netcat listener backend

Legal Notice
Developed strictly for educational laboratories and authenticated cybersecurity research.
