import ctypes
from pathlib import Path

class VigenereCipher:
    def __init__(self):
        # Đường dẫn: lùi 1 cấp từ tbstandard/ rồi vào bin/
        base_dir = Path(__file__).parent.parent
        dll_path = base_dir / "bin" / "vigenere.dll"
        
        if not dll_path.exists():
            raise FileNotFoundError(f"Tebee ơi, quên build DLL rồi nè: {dll_path}")
            
        self._lib = ctypes.CDLL(str(dll_path))
        self._initial_args()

    def _initial_args(self):
        # Cả encrypt và decrypt đều nhận (char*, char*)
        self._lib.vigenere_encrypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._lib.vigenere_encrypt.restype = None
        
        self._lib.vigenere_decrypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._lib.vigenere_decrypt.restype = None

    def encrypt(self, text: str, key: str) -> str:
        if not key: return text
        
        # Vì chúng ta sửa trực tiếp trên buffer (In-place)
        # nên cần tạo một buffer chứa bản sao của text
        buffer = ctypes.create_string_buffer(text.encode('utf-8'))
        key_bytes = key.encode('utf-8')
        
        self._lib.vigenere_encrypt(buffer, key_bytes)
        return buffer.value.decode('utf-8')

    def decrypt(self, text: str, key: str) -> str:
        if not key: return text
        
        buffer = ctypes.create_string_buffer(text.encode('utf-8'))
        key_bytes = key.encode('utf-8')
        
        self._lib.vigenere_decrypt(buffer, key_bytes)
        return buffer.value.decode('utf-8')