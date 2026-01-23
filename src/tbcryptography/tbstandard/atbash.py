import ctypes
from pathlib import Path

class AtbashCipher:
    def __init__(self):
        # Lấy thư mục hiện tại của tệp này
        base_dir = Path(__file__).parent.parent
        # Xây dựng đường dẫn đến thư viện DLL tại tbcryptography/bin/atbash.dll
        dll_path = base_dir / 'bin' / 'atbash.dll'
        self._lib = ctypes.CDLL(dll_path)
        self.initial_args()
    def initial_args(self):
        # Khởi tạo các đối số nếu cần thiết
        self._lib.atbash.argtypes = [ctypes.c_char_p]
        self._lib.atbash.restype = None

    def process(self, input_text: str) -> str:
        # Chuyển đổi chuỗi đầu vào thành bytes
        input_bytes = input_text.encode('utf-8')
        # Tạo một buffer để lưu trữ kết quả
        output_buffer = ctypes.create_string_buffer(len(input_bytes) + 1)
        # Gọi hàm từ DLL
        self._lib.atbash_process(ctypes.c_char_p(input_bytes), output_buffer)
        # Chuyển đổi kết quả từ bytes trở lại chuỗi
        return output_buffer.raw[:len(input_bytes)].decode('utf-8')