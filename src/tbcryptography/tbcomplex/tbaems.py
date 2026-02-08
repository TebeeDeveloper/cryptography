import ctypes
import os
from pathlib import Path
from typing import Final, Optional

class TBAEMS:
    _lib: Optional[ctypes.CDLL] = None

    def __init__(self, key_data: bytes) -> None:
        __base__ = Path(__file__).resolve().parent.parent
        dll_path = __base__ / "bin" / "tbaems.dll"
        
        # Thêm thư mục bin vào DLL path cho Windows
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(str(__base__ / "bin"))
            
        self.__lib__ = ctypes.CDLL(str(dll_path), winmode=0)
        self._setup_types()
        
        if len(key_data) < 32:
            raise ValueError("Key must be 32 bytes.")
        
        # Truyền Key dưới dạng mảng byte thô
        self._instance = self.__lib__.CreateAEMS(key_data)

    def _setup_types(self) -> None:
        # CreateAEMS: nhận con trỏ dữ liệu thô
        self.__lib__.CreateAEMS.argtypes = [ctypes.c_void_p]
        self.__lib__.CreateAEMS.restype = ctypes.c_void_p

        # Encrypt: tham số cuối là con trỏ uint8 (cho Nonce)
        self.__lib__.Encrypt.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_uint8), 
            ctypes.c_size_t, 
            ctypes.c_size_t,
            ctypes.c_void_p # Nonce pointer
        ]
        self.__lib__.Encrypt.restype = ctypes.c_size_t
        
        self.__lib__.Decrypt.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_uint8), 
            ctypes.c_size_t,
            ctypes.c_void_p
        ]
        self.__lib__.Decrypt.restype = ctypes.c_size_t

    @staticmethod
    def generate_key_256() -> bytes:
        __base__ = Path(__file__).resolve().parent.parent
        dll = ctypes.CDLL(str(__base__ / "bin" / "tbaems.dll"), winmode=0)
        buffer = (ctypes.c_uint8 * 32)()
        dll.GenerateKey256bit(buffer)
        return bytes(buffer)

    def encrypt(self, data: bytearray | memoryview, nonce: bytes) -> int:
        # Nếu data là memoryview, mình không thể dùng .extend()
        # Hare sẽ kiểm tra xem có cần padding không.
        length = len(data)
        
        # Nếu là memoryview, Hare khuyên Tebee nên pad từ file terminal.py 
        # trước khi đưa vào đây, hoặc convert tạm sang bytearray nếu bắt buộc
        if isinstance(data, memoryview):
            # Với memoryview, chúng ta giả định buffer đã đủ lớn hoặc không cần pad
            ptr = (ctypes.c_uint8 * length).from_buffer(data)
            return self.__lib__.Encrypt(self._instance, ptr, length, length, nonce)
        else:
            # Code cũ cho bytearray
            padded_length = ((length // 16) + 1) * 16
            data.extend(b'\x00' * (padded_length - length))
            ptr = (ctypes.c_uint8 * len(data)).from_buffer(data)
            return self.__lib__.Encrypt(self._instance, ptr, length, len(data), nonce)

    def decrypt(self, data: bytearray | memoryview, nonce: bytes) -> int:
        length = len(data)
        ptr = (ctypes.c_uint8 * length).from_buffer(data)
        # DLL sẽ sửa trực tiếp trên vùng nhớ của 'data'
        actual_size = self.__lib__.Decrypt(self._instance, ptr, length, nonce)
        return actual_size
