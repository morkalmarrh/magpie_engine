import googletrans
import random
import sys
from collections.abc import Generator
import re

def random_lang(blacklist: list) -> str:
    langs = [lang for lang in googletrans.LANGUAGES.keys() if 
             lang not in blacklist and lang !="en" and lang != "eo"]
    return random.choice(langs)

def parse_txt(file: str) -> list:
     with open(file, "r") as txt:
        return txt.readlines()
        
def get_words(line) -> Generator[str]:
    regex = re.compile('[,\.!?]')
    yield from [regex.sub('', word).strip() for word in line.split(" ")]

def mangler(word: str, translator: googletrans.Translator, 
            exhausted_langs = None) -> str:
    exhausted_langs = [] if not exhausted_langs else exhausted_langs
    lang = random_lang(blacklist = exhausted_langs)
    mangled_word = translator.translate(word, dest = lang).pronunciation
    if mangled_word:
        return mangled_word
    else:
        exhausted_langs.append(lang)
        return mangler(word, translator, exhausted_langs)
        
        
def get_new_lines(file: str) -> Generator[list]:
    lines = parse_txt(file)
    translator = googletrans.Translator()
    new_lines = []
    for line in lines:
        mangled_line = [mangler(word, translator) for word in get_words(line)]
        print(mangled_line)
        new_lines.append(" ".join(mangled_line))
        new_lines.append("\n")
    return new_lines

def dump_new_lines(infile: list, outfile: str):
    with open(outfile, "w+", encoding = "utf-8") as txt:
        txt.writelines(get_new_lines(infile))
        
def main():
    file = sys.argv[1]
    outfile = sys.argv[2]
    dump_new_lines(file, outfile)
    
if __name__ == "__main__":
    sys.exit(main())
    

