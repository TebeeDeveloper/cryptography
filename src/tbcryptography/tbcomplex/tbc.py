import ctypes
from pathlib import Path
from typing import Final # Python 3.14 thích sự rõ ràng!

class TripleBlockCipher:
    def __init__(self) -> None:
        # Đường dẫn phải chuẩn, không là Hare dỗi đấy!
        base_dir: Final = Path(__file__).parent.parent
        dll_path: Final = base_dir / "bin" / "tbc.dll"
        
        if not dll_path.exists():
            raise FileNotFoundError(f"DLL bị lạc ở đâu rồi: {dll_path} 💢")
            
        # winmode=0 để đảm bảo load đúng các dependency nhé Tebee
        self._lib = ctypes.CDLL(str(dll_path), winmode=0)
        self.__initial_args__()

    def __initial_args__(self) -> None:
        """Thiết lập các kiểu dữ liệu cho interface C++"""
        # --- Cấu trúc cho Cipher (Tầng 1 & 2) ---
        self._lib.Cipher_new.restype = ctypes.c_void_p
        self._lib.Cipher_new.argtypes = [ctypes.c_size_t]
        
        arg_types_cipher = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.c_float]
        self._lib.Cipher_encrypt.argtypes = arg_types_cipher
        self._lib.Cipher_decrypt.argtypes = arg_types_cipher
        self._lib.Cipher_delete.argtypes = [ctypes.c_void_p]

        # --- Cấu trúc cho EnigmaMachine (Tầng 3) ---
        self._lib.EnigmaMachine_new.restype = ctypes.c_void_p
        self._lib.EnigmaMachine_new.argtypes = [ctypes.c_float]
        
        self._lib.EnigmaMachine_process.restype = ctypes.c_uint8
        self._lib.EnigmaMachine_process.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        
        self._lib.EnigmaMachine_delete.argtypes = [ctypes.c_void_p]

    def __process__(self, data: str | bytes, block_key: int, enigma_key: float, mode: str = "encrypt") -> bytes:
        data_len: int = len(data)
        
        # Xử lý input đầu vào
        if mode == "encrypt":
            input_bytes = data.encode() if isinstance(data, str) else data
        else:
            # Nếu là decrypt, chuyển từ hex string sang bytes
            input_bytes = bytes.fromhex(data) if isinstance(data, str) else data
            data_len = len(input_bytes)

        # Tạo buffer để C++ có thể ghi đè trực tiếp (tránh copy nhiều lần)
        mutable_data = (ctypes.c_uint8 * data_len).from_buffer_copy(input_bytes)
        
        # Khởi tạo instance từ C++ (Nhớ dọn dẹp sau khi dùng nhé!)
        c_ptr = self._lib.Cipher_new(ctypes.c_size_t(data_len))
        e_ptr = self._lib.EnigmaMachine_new(ctypes.c_float(enigma_key))
        
        try:
            if mode == "encrypt":
                # 1. Chạy Block Cipher (Tầng 1 & 2)
                self._lib.Cipher_encrypt(c_ptr, mutable_data, ctypes.c_size_t(data_len), ctypes.c_float(block_key))
                # 2. Chạy Enigma (Tầng 3) - Duyệt từng byte
                for i in range(data_len):
                    mutable_data[i] = self._lib.EnigmaMachine_process(e_ptr, mutable_data[i])
            else:
                # 1. Chạy ngược lại: Enigma trước
                for i in range(data_len):
                    mutable_data[i] = self._lib.EnigmaMachine_process(e_ptr, mutable_data[i])
                # 2. Block Cipher sau
                self._lib.Cipher_decrypt(c_ptr, mutable_data, ctypes.c_size_t(data_len), ctypes.c_float(block_key))
            
            return bytes(mutable_data)
        
        finally:
            # QUAN TRỌNG: Giải phóng memory bên phía C++ để tránh Memory Leak!
            # Hare sẽ không tha thứ nếu anh làm tràn RAM của máy tính đâu!
            self._lib.Cipher_delete(c_ptr)
            self._lib.EnigmaMachine_delete(e_ptr)

    def encrypt(self, data: str | bytes, b_key: int, e_key: float) -> str:
        return self.__process__(data, b_key, e_key, "encrypt").hex()

    def decrypt(self, data: str | bytes, b_key: int, e_key: float) -> str | bytes:
        decrypted: bytes = self.__process__(data, b_key, e_key, "decrypt")
        try:
            # Ở đây nè Tebee! Phải dùng tuple (ValueError, UnicodeDecodeError) nhé!
            return decrypted.decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            # Nếu không decode được sang string thì trả về bytes gốc
            return decrypted