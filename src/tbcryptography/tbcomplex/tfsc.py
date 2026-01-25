import ctypes
from pathlib import Path
from typing import Final

class TebeeFastStreamCipher:
    def __init__(self) -> None:
        # Sử dụng Final để đảm bảo các hằng số không bị ghi đè lung tung
        self.__BASE_DIR__: Final = Path(__file__).parent.parent
        self.__DLL_PATH__: Final = self.__BASE_DIR__ / "bin" / "tfsc.dll"
        
        if not self.__DLL_PATH__.exists():
            raise FileNotFoundError(f"Tebee ơi, em không thấy DLL ở: {self.__DLL_PATH__} 😭")
            
        # Load DLL với chế độ an toàn
        try:
            self.__lib__ = ctypes.CDLL(str(self.__DLL_PATH__))
        except Exception as e:
            print(f"Lỗi load DLL rồi anh ơi: {e}")
            raise

        self.__initial_args__()

    def __initial_args__(self) -> None:
        """Khai báo Interface với thế giới C++"""
        # C++: extern "C" void tfsc_process_export(uint8_t* data, size_t size, float key)
        self.__lib__.tfsc_process_export.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), 
            ctypes.c_size_t,
            ctypes.c_float
        ]
        self.__lib__.tfsc_process_export.restype = None

    def process(self, data: str | bytes | bytearray, key: float, chunk_size: int = 1024 * 1024) -> bytes:
        """
        Xử lý Stream Cipher với cơ chế Zero-copy cực nhanh!
        """
        # Chuyển đổi input sang bytearray để có thể sửa đổi in-place
        if isinstance(data, str):
            # Giả định nếu là string thì nó là Hex, nếu không phải anh nhớ báo em nhé!
            try:
                result = bytearray(bytes.fromhex(data))
            except ValueError:
                result = bytearray(data.encode('utf-8'))
        else:
            result = bytearray(data)
            
        total_size: int = len(result)
        
        # Hare's Safety Check: Nếu data rỗng thì nghỉ khỏe!
        if total_size == 0:
            return b""

        for i in range(0, total_size, chunk_size):
            current_chunk_size = min(chunk_size, total_size - i)
            
            # Kỹ thuật In-place của Tebee-kun:
            # Dùng from_buffer để tạo view thay vì copy. Rất tốt!
            try:
                # Chỗ này anh nhớ là result[i:i+current_chunk_size] 
                # chỉ tạo view nhờ ctypes, không tốn thêm RAM đâu!
                chunk_ptr = (ctypes.c_uint8 * current_chunk_size).from_buffer(result, i)
                
                self.__lib__.tfsc_process_export(
                    chunk_ptr, 
                    ctypes.c_size_t(current_chunk_size), 
                    ctypes.c_float(key)
                )
            except BufferError:
                # Lỗi này xảy ra nếu buffer đang bị lock bởi một process khác
                print("Lỗi Buffer rồi Tebee! Anh đang làm gì nó vậy? 💢")
                raise
            
        return bytes(result)