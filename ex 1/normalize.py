import re
import os


CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "u", "ya", "ye", "yi", "g")

Trans = dict()
for cyr, lat in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    Trans[ord(cyr)] = lat
    Trans[ord(cyr.upper())] = lat.upper()

def normalize(name):
    base, ext = os.path.splitext(name)
    base = re.sub(r'\W', '_', base.translate(Trans))
    return f'{base}{ext}'