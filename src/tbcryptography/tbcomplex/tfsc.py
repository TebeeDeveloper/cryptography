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
        self.__lib__.tfsc_encrypt.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), 
            ctypes.c_size_t,
            ctypes.c_float
        ]
        self.__lib__.tfsc_encrypt.restype = ctypes.c_size_t
        
        self.__lib__.tfsc_decrypt.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.c_float
        ]
        self.__lib__.tfsc_decrypt.restype = ctypes.c_size_t

    def encrypt(self, data: str | bytes | bytearray, key: float) -> bytes:
        """Mã hóa trực tiếp trên buffer cũ, trả về độ dài mới"""
        original_len = len(data)
        padded_len = original_len if original_len % 16 == 0 else ((original_len // 16) + 1) * 16
        
        # Mở rộng buffer nếu cần (chỉ tốn thêm vài bytes padding)
        if len(data) < padded_len:
            data.extend(b'\x00' * (padded_len - original_len))

        # Trỏ thẳng vào RAM của bytearray
        c_buffer = (ctypes.c_uint8 * len(data)).from_buffer(data)
        
        # C++ xử lý thẳng trên vùng nhớ này
        new_size = self.__lib__.tfsc_encrypt(
            ctypes.cast(c_buffer, ctypes.POINTER(ctypes.c_uint8)),
            ctypes.c_size_t(original_len),
            ctypes.c_float(key)
        )
        return new_size # Chỉ trả về kích thước, dữ liệu nằm sẵn trong 'data' rồi!

    def decrypt(self, data: bytes | bytearray, key: float) -> bytes:
        # Dữ liệu giải mã phải luôn là bội số của 16
        if len(data) % 16 != 0:
            raise ValueError("Tebee ơi, dữ liệu này không đúng kích thước block 16 bytes rồi!")

        # Copy ra một bản tạm để xử lý trên RAM
        process_buffer = bytearray(data)
        c_buffer = (ctypes.c_uint8 * len(process_buffer)).from_buffer(process_buffer)

        # Gọi C++ để giải mã và gỡ padding
        actual_size = self.__lib__.tfsc_decrypt(
            ctypes.cast(c_buffer, ctypes.POINTER(ctypes.c_uint8)),
            ctypes.c_size_t(len(process_buffer)),
            ctypes.c_float(key)
        )

        # Cắt bỏ phần padding dư thừa dựa trên size trả về từ C++
        return bytes(process_buffer[:actual_size])