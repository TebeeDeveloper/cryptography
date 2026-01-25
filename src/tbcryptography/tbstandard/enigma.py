from base64 import b85encode, b85decode
import random

# Tebee-kun nhìn nè, đây là bảng chữ cái Base85 (RFC 1924)
# Em định nghĩa nó như một hằng số để tránh "Magic Strings" nhé!
BASE85_CHARS = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "!#$%&()*+-;<=>?@^_`{|}~"
)

class EnigmaRotor:
    def __init__(self, mapping: str, ring_setting: int = 0):
        # Type Hinting đầy đủ nha Tebee! 
        self.forward_map = mapping
        # Tạo map ngược để quay về cho nhanh, tối ưu hiệu năng đó!
        self.backward_map = "".join(
            BASE85_CHARS[mapping.find(c)] for c in BASE85_CHARS
        )
        self.position = ring_setting

    def rotate(self) -> bool:
        """Xoay rotor và trả về True nếu hoàn thành một vòng."""
        self.position = (self.position + 1) % 85
        return self.position == 0

    def encode(self, char_idx: int, reverse: bool = False) -> int:
        """Mã hóa một ký tự dựa trên vị trí hiện tại."""
        shift_map = self.backward_map if reverse else self.forward_map
        
        # Tính toán index sau khi cộng offset của rotor
        entering = (char_idx + self.position) % 85
        out_char = shift_map[entering]
        exit_idx = (BASE85_CHARS.find(out_char) - self.position) % 85
        return exit_idx

class EnigmaMachine:
    def __init__(self, seed: int):
        # Chúng ta dùng seed để tạo các Rotor ngẫu nhiên nhưng có thể tái tạo được
        rng = random.Random(seed)
        
        # Tạo 3 rotor hoán vị ngẫu nhiên từ bảng Base85
        shuffled = list(BASE85_CHARS)
        
        self.rotors = []
        for _ in range(3):
            rng.shuffle(shuffled)
            self.rotors.append(EnigmaRotor("".join(shuffled)))
            
        # Reflector: Phải là các cặp hoán vị đối xứng (A->B thì B->A)
        reflector_list = list(range(85))
        rng.shuffle(reflector_list)
        self.reflector = {}
        # Em tạo cặp cho reflector nè, Tebee thấy em thông minh chưa?
        for i in range(0, 84, 2):
            self.reflector[reflector_list[i]] = reflector_list[i+1]
            self.reflector[reflector_list[i+1]] = reflector_list[i]
        # Ký tự cuối cùng tự trỏ vào chính nó nếu lẻ (85 là số lẻ mà)
        if 84 not in self.reflector: self.reflector[84] = 84

    def process_text(self, text: str) -> str:
        result = []
        for char in text:
            if char not in BASE85_CHARS:
                result.append(char) # Giữ nguyên nếu không nằm trong bảng mã
                continue
                
            # 1. Xoay các Rotor (Cơ chế giống đồng hồ)
            if self.rotors[0].rotate():
                if self.rotors[1].rotate():
                    self.rotors[2].rotate()
            
            # 2. Đi qua 3 rotor (Chiều đi)
            idx = BASE85_CHARS.find(char)
            for r in self.rotors:
                idx = r.encode(idx)
                
            # 3. Phản xạ (Reflector)
            idx = self.reflector[idx]
            
            # 4. Đi ngược lại qua 3 rotor (Chiều về)
            for r in reversed(self.rotors):
                idx = r.encode(idx, reverse=True)
                
            result.append(BASE85_CHARS[idx])
            
        return "".join(result)