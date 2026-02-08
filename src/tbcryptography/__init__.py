from .tbstandard.atbash import AtbashCipher
from .tbstandard.caesar import CaesarCipher
from .tbstandard.enigma import EnigmaMachine
from .tbstandard.vigenere import VigenereCipher

from .tbcomplex.tbc import TripleBlockCipher
from .tbcomplex.tfsc import TebeeFastStreamCipher
from .tbcomplex.tbaems import TBAEMS

atbash = AtbashCipher()
caesar = CaesarCipher()
vigenere = VigenereCipher()

tbc = TripleBlockCipher()
tfsc = TebeeFastStreamCipher()

__author__ = "Tebee 9/4"
__all__ = ["atbash", "caesar", "enigma", "vigenere", "tbc", "tfsc", "tbaems"]