import googletrans
import random
import sys
from collections.abc import Generator
import re
import pronouncing, cmudict

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

def get_syllables(word):
    phones = pronouncing.phones_for_word(word)
    return sum([pronouncing.syllable_count(p) for p in phones])

def pronounce_natural(phones: list) -> str:
    phones_str = "".join(phones) 
    return re.sub(r'\d+', '', phones_str)

def trunc_word(phones: list, target_sylls: int) -> str:
    slice_num = target_sylls - 1
    return phones[:slice_num]
    
def match_syllables(before: list, after: list) -> str:
    def syll_count(phones):
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
                
def get_mangled_lines(file: str) -> Generator[list]:
    lines = parse_txt(file)
    translator = googletrans.Translator()
    mangled_lines = []
    for line in lines:
        mangled_line = [mangler(word, translator) for word in get_words(line)]
        mangled_lines.append(mangled_line)
    return lines, mangled_lines

def dump_new_lines(lines: list, outfile: str):
    with open(outfile, "w+", encoding = "utf-8") as txt:
        txt.writelines(lines)
        
def main():
    file = sys.argv[1]
    outfile = sys.argv[2]
    befores, afters = get_mangled_lines(file)
    cleaned_lines = []
    #The cmudict isn't able to guess phonemes from non-English words.
    #for before, after in zip(befores, afters):
    #    cleaned_lines.append(match_syllables(before.split(), after) + "\n")
    for line in afters:
        cleaned_lines.append(" ".join(line))
    dump_new_lines(cleaned_lines, outfile)
     
if __name__ == "__main__":
    sys.exit(main())
    

