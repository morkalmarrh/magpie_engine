import googletrans
import random
import sys
from collections.abc import Generator
import re
import pronouncing, cmudict
from wanakana import to_hiragana, is_romaji, is_hiragana

translator = googletrans.Translator()

def random_lang(blacklist: list) -> str:
    blacklist.extend(["en", "eo"])
    langs = [lang for lang in googletrans.LANGUAGES.keys() if 
             lang not in blacklist]
    return random.choice(langs)

def parse_txt(file: str) -> list:
     with open(file, "r") as txt:
        return txt.readlines()
        
def get_words(line) -> Generator[str]:
    regex = re.compile('[,\.!?]')
    yield from [regex.sub('', word).strip() for word in line.split(" ")]

def random_translate(word: str, 
            exhausted_langs = None) -> str:
    exhausted_langs = [] if not exhausted_langs else exhausted_langs
    lang = random_lang(blacklist = exhausted_langs)
    trans_word = translator.translate(word, src = "en", dest = lang).pronunciation
    if trans_word:
        return trans_word
    else:
        exhausted_langs.append(lang)
        return random_translate(word, exhausted_langs)

def get_syllables(word: str) -> int:
    phones = pronouncing.phones_for_word(word)
    return sum([pronouncing.syllable_count(p) for p in phones])

def pronounce_natural(phones: list) -> Generator[str]:
    phones_str = "".join(phones) 
    yield re.sub(r'\d+', '', phones_str)

def trunc_word(phones: list, target_sylls: int) -> Generator[str]:
    slice_num = target_sylls - 1
    yield from phones[:slice_num]
    
def match_syllables(before: list, after: list) -> str:
    def syll_count(phones: list) -> int:
        return sum([pronouncing.syllable_count(p) for p in phones])   
    cleaned_line = []
    for b, a in zip(before, after):
        b_phones = pronouncing.phones_for_word(b)
        a_phones = pronouncing.phones_for_word(a)
        b_count, a_count = syll_count(b_phones), syll_count(a_phones)
        if a_count > b_count: 
            a_phones = trunc_word(a_phones, b_count)
        cleaned_line.append(pronounce_natural(a_phones))
    return " ".join(cleaned_line)
               
def get_mangled_lines(file: str) -> Generator[str]:
    lines = parse_txt(file)
    for line in lines:
        if line.strip():
            yield " ".join([random_translate(word) for word in get_words(line)])

def dump_new_lines(lines: list, outfile: str):
    for i, line in enumerate(lines):
        if not line.endswith("\n"):
            lines[i] = line + "\n"
    with open(outfile, "w+", encoding = "utf-8") as txt:
        txt.writelines(lines)
            
def mangled_to_hiragana(line: str) -> Generator[str]:
    en_line = [translator.translate(word, dest = "en").text 
               for word in line.split()]
    for word in en_line:
        if is_romaji(word):
            yield clean_hiragana(to_hiragana(word))
        else:
            continue   

def clean_hiragana(word: str) -> str:
    return "".join([letter for letter in word if is_hiragana(letter)])
    
def main():
    file = sys.argv[1]
    outfile = sys.argv[2]
    mangled_lines = [line for line in get_mangled_lines(file)]
    dump_new_lines(mangled_lines, outfile)
    jp_lines = []
    for line in mangled_lines:
        jp_lines.append(" ".join([word for word in mangled_to_hiragana(line)]))
    dump_new_lines(jp_lines, "jp_dump.txt")
     
if __name__ == "__main__":
    sys.exit(main())