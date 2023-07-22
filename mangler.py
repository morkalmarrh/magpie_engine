import googletrans
import random
import sys
from collections.abc import Generator
import re
from wanakana import to_hiragana, is_romaji, is_hiragana

translator = googletrans.Translator()
INVALID = ("ぅ", "ぃ", "ぇ", "ぁ", "ぉ", "ゃ", "っ", "ー", "ょ")

def random_lang(blacklist: list) -> str:
    blacklist.extend(["en", "eo"])
    langs = [lang for lang in googletrans.LANGUAGES.keys() if 
             lang not in blacklist]
    return random.choice(langs)

def parse_txt(file: str) -> Generator[str]:
     with open(file, "r", encoding = "utf-8") as txt:
        return (line.strip() for line in txt.readlines())
        
def get_words(line) -> Generator[str]:
    regex = re.compile('[,\.!?]')
    yield from [" ".join(re.sub(regex, '', word).split("-")) for word in line.split()]

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
               
def get_mangled_lines(file: str) -> Generator[str]:
    lines = parse_txt(file)
    for line in lines:
        if line.strip():
            yield " ".join([random_translate(word) 
                            for word in get_words(line) if word])

def clean_line(line: str) -> str:
    line = line.replace(".", "")
    while '  ' in line:
        line =  re.sub('\s+',' ', line)
    return line.strip(" ") + ".\n"


def dump_new_lines(lines: list, outfile: str):
    for i, line in enumerate(lines):
        lines[i] = clean_line(line)
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
    return "".join([letter for letter in word if is_hiragana(letter) 
                    and letter not in INVALID])

def main():
    file = sys.argv[1]
    outfile = sys.argv[2]
    mangled_lines = [line for line in get_mangled_lines(file)]
    dump_new_lines(mangled_lines, outfile)
    hiragana_lines = [(" ".join([word for word in mangled_to_hiragana(line)]))
                      for line in mangled_lines if line]
    dump_new_lines(hiragana_lines, "jp_dump.txt")
     
if __name__ == "__main__":
    sys.exit(main())