import ctypes
from pathlib import Path

class TebeeFastStreamCipher:
    def __init__(self):
        base_dir = Path(__file__).parent.parent
        dll_path = base_dir / "bin" / "tfsc.dll"
        
        if not dll_path.exists():
            raise FileNotFoundError(f"Không thấy DLL tại: {dll_path}")
            
        self._lib = ctypes.CDLL(str(dll_path))
        self.__initial_args__()

    def __initial_args__(self):
        # Giả sử anh dùng uint64 cho key của Stream Cipher để bảo mật hơn nhé!
        self._lib.tfsc_process_export.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), 
            ctypes.c_size_t,
            ctypes.c_float  # Anh đổi lại thành c_float nếu DLL nhận float nha!
        ]
        self._lib.tfsc_process_export.restype = None

    def process(self, data: str | bytes, key: int, chunk_size: int = 1024 * 1024) -> bytes:
        # Chuẩn bị dữ liệu mutable (có thể thay đổi tại chỗ)
        if isinstance(data, str):
            result = bytearray(data.encode('utf-8'))
        else:
            result = bytearray(data)
            
        total_size = len(result)
        
        for i in range(0, total_size, chunk_size):
            current_chunk_size = min(chunk_size, total_size - i)
            
            # Kỹ thuật thượng thừa: Trỏ pointer trực tiếp vào offset i của result
            # Không tạo bản sao, cực kỳ tiết kiệm bộ nhớ!
            chunk_ptr = (ctypes.c_uint8 * current_chunk_size).from_buffer(result, i)
            
            # Gọi hàm DLL xử lý In-place
            self._lib.tfsc_process_export(
                chunk_ptr, 
                ctypes.c_size_t(current_chunk_size), 
                ctypes.c_float(key)
            )
            
        return bytes(result)