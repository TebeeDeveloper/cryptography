import ctypes
from pathlib import Path

class EnigmaCipher:
    def __init__(self):
        # Lùi 1 cấp từ tbstandard/ để tìm thư mục bin/
        base_dir = Path(__file__).parent.parent
        dll_path = base_dir / "bin" / "enigma.dll"
        
        # Kiểm tra file tồn tại để tránh crash "vô tri" nè
        if not dll_path.exists():
            raise FileNotFoundError(f"Tebee ơi, em không tìm thấy file tại: {dll_path}")
            
        self._lib = ctypes.CDLL(str(dll_path))
        self.initial_args()

    def initial_args(self):
        # Tham số: input (chuỗi C), output (buffer ký tự)
        self._lib.process.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._lib.process.restype = None

    def process(self, plaintext: str) -> str:
        if not plaintext:
            return ""

        input_bytes = plaintext.encode("utf-8")
        # Enigma thường có đầu ra bằng độ dài đầu vào
        # Cộng 1 cho ký tự kết thúc chuỗi \0
        output_buffer = ctypes.create_string_buffer(len(input_bytes) + 1)
        
        try:
            self._lib.process(
                ctypes.c_char_p(input_bytes), 
                output_buffer
            )
            
            # Lấy giá trị từ buffer và decode
            return output_buffer.value.decode("utf-8")
        except Exception as e:
            return f"Lỗi cỗ máy Enigma rồi Tebee ơi: {e}"