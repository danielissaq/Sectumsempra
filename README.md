Sectumsempra v1.0

Sectumsempra is an automated attack script and payload framework engineered for CTF challenges. It takes target parameters and crafts multi platform scripts to capture reverse shells and handle privilege escalation.

Complete Attack Workflow

Follow these exact steps to use NetWeave and Sectumsempra together in a TryHackMe room.

Step 1 Scout the Target with NetWeave
Run your reconnaissance framework to find the exploit path
python pwn_recon.py
Input the target IP when prompted. NetWeave will scan open web ports and output the best entry point under the section THE GOLDEN PATH.

Step 2 Fire up Sectumsempra
Launch this framework to build your attack payload files
python3 sectumsempra.py
1. Input the same target IP address.
2. Press Enter to use the default listener port 4444.
The script automatically builds two tailored exploit deployment assets in your folder:
- sectum_linux_strike_[IP].sh
- sectum_win_strike_[IP].ps1

Step 3 Start Your Netcat Listener
Open a separate terminal window or tab in Kali and start the listener to catch the connection
nc -lvnp 4444

Step 4 Execute the Exploit
Deploy the commands generated inside your strike files against the vulnerability found by NetWeave. 

Step 5 Catch the Shell and Escalate
Once the target connects back to your Netcat terminal, you have initial access. Run the pre staged command displayed in your terminal to download and execute local privilege escalation scanners to find and grab the root flags immediately.

Deployment
git clone https://github.com
cd Sectumsempra
python3 -m venv .venv
source .venv/bin/activate
pip install netifaces

Requirements
Python 3.10 plus
netifaces library
Netcat listener backend

Legal Notice
Developed strictly for educational laboratories and authenticated cybersecurity research.
