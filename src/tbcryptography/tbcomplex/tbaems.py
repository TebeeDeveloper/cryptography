import ctypes
import os
from pathlib import Path
from typing import Final, Optional

class TBAEMS:
    # Biến class để lưu handle thư viện, tránh nạp đi nạp lại nhiều lần
    _lib: Optional[ctypes.CDLL] = None

    def __init__(self, key_data: bytes) -> None:
        # ... (Phần xác định Path và Load DLL giữ nguyên nhé) ...
        __base__: Final = Path(__file__).resolve().parent.parent
        dll_dir: Final = __base__ / "bin"
        dll_path: Final = dll_dir / "tbaems.dll"

        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(str(dll_dir))

        try:
            self.__lib__ = ctypes.CDLL(str(dll_path), winmode=0)
        except OSError as e:
            raise e

        self._setup_types()
        
        # --- SỬA TỪ ĐÂY NÈ TEBEE ---
        if len(key_data) < 32:
            raise ValueError("Tebee ơi, Key phải đủ 32 bytes chứ! (╬ Ò﹏Ó)")

        # CHỈ GỌI MỘT LẦN DUY NHẤT VÀ TRUYỀN TRỰC TIẾP key_data
        # Python bytes sẽ tự động biến thành const void* an toàn cho C++
        self._instance = self.__lib__.CreateAEMS(key_data)

        if not self._instance:
            raise MemoryError("Tebee ơi, C++ không cấp phát được bộ nhớ cho AEMS rồi!")
        # --- HẾT PHẦN SỬA ---

    def _setup_types(self) -> None:
        """Định nghĩa kiểu dữ liệu để C++ và Python hiểu nhau"""
        # CreateAEMS(const void*) -> void*
        self.__lib__.CreateAEMS.argtypes = [ctypes.c_void_p]
        self.__lib__.CreateAEMS.restype = ctypes.c_void_p
        
        # Encrypt & Decrypt: (instance, data_ptr, length)
        FORMAT = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.__lib__.Encrypt.argtypes = FORMAT
        self.__lib__.Encrypt.restype = ctypes.c_size_t
        
        self.__lib__.Decrypt.argtypes = FORMAT
        self.__lib__.Decrypt.restype = ctypes.c_size_t
        
        # DeleteAEMS(void*)
        self.__lib__.DeleteAEMS.argtypes = [ctypes.c_void_p]
        self.__lib__.DeleteAEMS.restype = None

    @classmethod
    def _get_lib(cls) -> ctypes.CDLL:
        """Nạp DLL cho các hàm dùng chung (Static Methods)"""
        if cls._lib is None:
            __base__ = Path(__file__).resolve().parent.parent
            dll_path = __base__ / "bin" / "tbaems.dll"
            cls._lib = ctypes.CDLL(str(dll_path), winmode=0)
            cls._lib.GenerateKey256bit.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
            cls._lib.GenerateKey256bit.restype = None
        return cls._lib

    @staticmethod
    def generate_key_256() -> bytes:
        """Sinh key 256-bit ngẫu nhiên từ C++"""
        lib = TBAEMS._get_lib()
        # Tạo mảng 32 phần tử uint8
        buffer = (ctypes.c_uint8 * 32)()
        lib.GenerateKey256bit(buffer)
        return bytes(buffer)
    
    def pad(self, data: bytes) -> bytes:
        # 1. Thêm byte 0x80
        data += b'\x80'
        # 2. Thêm 0x00 cho đến khi chia hết cho 16
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    def unpad(self, data: bytes) -> bytes:
        # Tìm vị trí byte 0x80 cuối cùng từ phải sang
        idx = data.rfind(b'\x80')
        if idx != -1:
            return data[:idx]
        return data

    def encrypt(self, data: bytearray) -> int:
        length = len(data)
        padded_length = ((length // 16) + 1) * 16
        
        # Nới rộng bytearray để C++ có chỗ ghi thêm Pad (vô cùng tiết kiệm RAM!)
        data.extend(b'\x00' * (padded_length - length))
        
        
        # Lấy pointer trực tiếp từ bytearray của Python
        ptr = (ctypes.c_uint8 * len(data)).from_buffer(data)
        
        # Gọi C++ xử lý in-place trên chính vùng nhớ đó
        new_size = self.__lib__.Encrypt(self._instance, ptr, length)
        return new_size

    def decrypt(self, encrypted_data: bytes) -> bytes:
        # 1. Tạo buffer từ dữ liệu đã mã hóa
        buffer = ctypes.create_string_buffer(encrypted_data, len(encrypted_data))
        ptr = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint8))
        
        # 2. C++ giải mã và Unpad, trả về độ dài thực tế ban đầu
        actual_size = self.__lib__.Decrypt(self._instance, ptr, len(encrypted_data))
        
        
        # 3. CỰC KỲ QUAN TRỌNG: Chỉ lấy đúng actual_size bytes
        # Dùng .raw sẽ lấy toàn bộ vùng nhớ, nên phải cắt chính xác!
        return buffer.raw[:actual_size]

    def __del__(self) -> None:
        """Hàm hủy để tránh Memory Leak (Cực kỳ quan trọng!)"""
        if hasattr(self, '_instance') and self._instance:
            self.__lib__.DeleteAEMS(self._instance)


if __name__ == "__main__":
    
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from tbcryptography import tfsc
    import time
    
    data = bytearray(1024*1024*512)
    def aes_():
        key = AESGCM.generate_key(256)
        nonce = os.urandom(12)
        
        aes = AESGCM(key)
        
        start = time.perf_counter()
        aes.encrypt(nonce, data, None)
        end = time.perf_counter()
        
        print(f"AES-256")
        print(f"Thời gian mã hóa: {end-start:.4f}")

    def tbaems_():
        key = TBAEMS.generate_key_256()
        
        tbaems = TBAEMS(key)
        
        start = time.perf_counter()
        tbaems.encrypt(data)
        end = time.perf_counter()
        
        print(f"TB_AEMS-256")
        print(f"Thời gian mã hóa: {end-start:.4f}")
    
    def tbfs_():
        start = time.perf_counter()
        tfsc.encrypt(data, os.urandom(128))
        end = time.perf_counter()
        
        print("TFSC-1024")
        print(f"Thời gian mã hóa: {end-start:.4f}")

    aes_()

    try:
        tbaems_()
    except Exception as e:
        print(e)

    tbfs_()