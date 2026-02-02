import sys
import os
import ctypes
from binascii import hexlify, unhexlify

# Thêm đường dẫn tới class AEMS của anh
from tbcryptography.tbcomplex.tbaems import TBAEMS  # Đảm bảo file tbaems.py nằm cùng thư mục

class TBAEMS_Terminal(ctypes.Structure):
    def __init__(self):
        self.key = None
        self.cipher = None
        self.prompt = "TBAEMS > "

    def start(self):
        print("="*50)
        print("TBAEMS TERMINAL v1.0 - ENCRYPTION SYSTEM")
        print("Type \\help to see available commands")
        print("="*50)
        
        while True:
            try:
                cmd_input = input(self.prompt).strip()
                if not cmd_input: continue
                
                parts = cmd_input.split()
                cmd = parts[0].lower()

                if cmd == "\\quit":
                    print("Exiting... Bye Tebee!")
                    break
                elif cmd == "\\create" and len(parts) > 1 and parts[1] == "key":
                    self.create_key()
                elif cmd == "\\getkey":
                    self.get_key()
                elif cmd == "\\encrypt":
                    self.do_encrypt()
                elif cmd == "\\decrypt":
                    self.do_decrypt()
                elif cmd == "\\help":
                    self.show_help()
                else:
                    print(f"Unknown command: {cmd}")
            except Exception as e:
                print(f"Error: {str(e)}")

    def create_key(self):
        # Tạo key 32 bytes ngẫu nhiên
        self.key = os.urandom(32)
        self.cipher = AEMS(self.key) # Khởi tạo engine với key mới
        print(f"[SUCCESS] New 256-bit key created and loaded.")

    def get_key(self):
        if self.key:
            print(f"Current Key (Hex): {hexlify(self.key).decode()}")
        else:
            print("[ERROR] No key loaded. Use \\create key first.")

    def do_encrypt(self):
        if not self.cipher:
            print("[ERROR] Please create a key first!"); return
        
        plaintext = input("Enter text to encrypt: ").encode()
        nonce = os.urandom(16) # Tạo Nonce ngẫu nhiên
        
        # Padding dữ liệu
        padded_data = bytearray(self.cipher.pad(plaintext))
        
        # Gọi engine C++ để mã hóa
        # Giả sử hàm encrypt của anh trả về dữ liệu đã mã hóa
        self.cipher.encrypt(padded_data, nonce) 
        
        print(f"Nonce: {hexlify(nonce).decode()}")
        print(f"Ciphertext: {hexlify(padded_data).decode()}")

    def do_decrypt(self):
        if not self.cipher:
            print("[ERROR] Please create a key first!"); return
            
        hex_data = input("Enter hex ciphertext: ")
        hex_nonce = input("Enter hex nonce: ")
        
        try:
            data = bytearray(unhexlify(hex_data))
            nonce = unhexlify(hex_nonce)
            
            # Giải mã
            decrypted = self.cipher.decrypt(data, nonce)
            print(f"Decrypted text: {decrypted.decode('utf-8', errors='replace')}")
        except:
            print("[ERROR] Invalid hex format or decryption failed.")

    def show_help(self):
        print("""
Available Commands:
  \\create key  : Generate and load a new 256-bit key
  \\getkey      : Show current session key
  \\encrypt     : Encrypt a string input
  \\decrypt     : Decrypt a hex string
  \\quit        : Exit terminal
        """)

if __name__ == "__main__":
    term = TBAEMS_Terminal()
    term.start()