import ctypes
from pathlib import Path

class CaesarCipher:
    def __init__(self):
        # Lùi ra 1 cấp từ tbstandard/ để vào bin/
        base_dir = Path(__file__).parent.parent 
        dll_path = base_dir / "bin" / "caesar.dll"
        
        # Dùng CDLL nếu anh không chắc về __stdcall, hoặc WinDLL nếu có dùng nó
        self._lib = ctypes.CDLL(str(dll_path)) 
        self.initial_args()

    def initial_args(self):
        # 3 tham số: input (bytes), shift (int), output (buffer)
        self._lib.process.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        self._lib.process.restype = None

    def process(self, input_text: str, shift: int) -> str:
        input_bytes = input_text.encode("utf-8")
        data_len = len(input_bytes)
        
        # Tạo buffer lưu kết quả
        output_buffer = ctypes.create_string_buffer(data_len)
        
        # Truyền đủ 3 món cho em!
        self._lib.process(
            input_bytes, 
            ctypes.c_int(shift), 
            output_buffer
        )
        
        return output_buffer.raw[:data_len].decode("utf-8")