import googletrans
import random, sys, os
from collections.abc import Generator
import re
from wanakana import to_hiragana, is_romaji, is_hiragana
from dataclasses import dataclass

translator = googletrans.Translator()
INVALID = ("ぅ", "ぃ", "ぇ", "ぁ", "ぉ", "ゃ", "っ", "ー", "ょ", "ゅ")

@dataclass
class Mangler():
    in_file: str
    out_file: str
    
    def __post_init__(self):
        self.blacklist = ["en", "eo"]
        
    def random_lang(self) -> str:
        langs = [lang for lang in googletrans.LANGUAGES.keys() if 
                 lang not in self.blacklist]
        return random.choice(langs)
    
    @staticmethod
    def parse_txt(file: str) -> Generator[str]:
         with open(file, "r", encoding = "utf-8") as txt:
            return (line.strip() for line in txt.readlines())
    
    @staticmethod
    def get_words(line) -> Generator[str]:
        regex = re.compile('[,\.!?]')
        yield from [" ".join(re.sub(regex, '', word).split("-")) for word in line.split()]

    def random_translate(self, word: str) -> str:
        lang = self.random_lang()
        trans_word = translator.translate(word, src = "en", 
                                          dest = lang).pronunciation
        if trans_word:
            return trans_word
        else:
            self.blacklist.append(lang)
            return self.random_translate(word)
    
    def get_mangled_lines(self) -> Generator[str]:
        lines = self.parse_txt(self.in_file)
        for line in lines:
            if line.strip():
                yield " ".join([self.random_translate(word) 
                                for word in self.get_words(line) if word])
                                
    @staticmethod
    def clean_line(line: str) -> str:
        line = line.replace(".", "")
        while '  ' in line:
            line =  re.sub('\s+',' ', line)
        return line.strip(" ") + "\n"

    def dump_new_lines(self, lines) -> None:
        for i, line in enumerate(lines):
            lines[i] = self.clean_line(line)
        with open(self.out_file, "w+", encoding = "utf-8") as txt:
            txt.writelines(lines)
    
    @staticmethod
    def mangled_to_hiragana(line: str) -> Generator[str]:
        en_line = [translator.translate(word, dest = "en").text 
                   for word in line.split()]
        for word in en_line:
            if is_romaji(word):
                yield Mangler.clean_hiragana(to_hiragana(word))
            else:
                continue 
                
    @staticmethod
    def clean_hiragana(word: str) -> str:
        return "".join([letter for letter in word if is_hiragana(letter) 
                        and letter not in INVALID])

def main():
    file = sys.argv[1]
    outfile = sys.argv[2]
    mangler = Mangler(file, outfile)
    mangled_lines = [line for line in mangler.get_mangled_lines()]
    hiragana_lines = [(" ".join([word for word in 
                      mangler.mangled_to_hiragana(line)]))
                      for line in mangled_lines if line]
    jp_out = os.path.splitext(os.path.basename(outfile)) + "_jp.txt"
    mangler.dump_new_lines(hiragana_lines,jp_out )
     
if __name__ == "__main__":
    sys.exit(main())