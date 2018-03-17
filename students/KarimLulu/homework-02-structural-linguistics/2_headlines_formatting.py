from pathlib import Path
import regex as re
import spacy
from spacy.tokenizer import Tokenizer
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

path = Path(__file__).resolve().parent
data_dir = path.parents[2] / "tasks" / "02-structural-linguistics"
filename = "examiner-headlines.txt"
output_filename = "output-formatting-headlines.txt"
nlp = spacy.load('en')

infixes = ('\\.\\.+',
           '…',
           '[\\p{So}]',
           '(?<=[0-9])[+\\\*^](?=[0-9])',
           '(?<=[[[\\p{Ll}&&\\p{Latin}]||[ёа-я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]])\\.(?=[[[\\p{Lu}&&\\p{Latin}]||[ЁА-Я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]])',
           '(?<=[[[\\p{Lu}&&\\p{Latin}]||[ЁА-Я]||[\\p{Ll}&&\\p{Latin}]||[ёа-я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]]),(?=[[[\\p{Lu}&&\\p{Latin}]||[ЁА-Я]||[\\p{Ll}&&\\p{Latin}]||[ёа-я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]])',
           '(?<=[[[\\p{Lu}&&\\p{Latin}]||[ЁА-Я]||[\\p{Ll}&&\\p{Latin}]||[ёа-я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]])[?";:=,.]*(?:–|—|--|---|——|~)(?=[[[\\p{Lu}&&\\p{Latin}]||[ЁА-Я]||[\\p{Ll}&&\\p{Latin}]||[ёа-я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]])',
           '(?<=[[[\\p{Lu}&&\\p{Latin}]||[ЁА-Я]||[\\p{Ll}&&\\p{Latin}]||[ёа-я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]"])[:<>=/](?=[[[\\p{Lu}&&\\p{Latin}]||[ЁА-Я]||[\\p{Ll}&&\\p{Latin}]||[ёа-я]||[\\p{L}&&\\p{Bengali}]||[\\p{L}&&\\p{Hebrew}]||[\\p{L}&&\\p{Arabic}]]])')
prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
infix_re = spacy.util.compile_infix_regex(infixes) #re.compile(r'''[~]''')

def custom_tokenizer(nlp):
    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                     suffix_search=suffix_re.search,
                     infix_finditer=infix_re.finditer)

nlp.tokenizer = custom_tokenizer(nlp)
CAPS = ["NOUN", "PRON", "PROPN", "ADJ", "ADV", "VERB", "SCONJ"]

def format_headline(text):
    doc = nlp(text)
    output = []
    for token in doc:
        if "-" in token.text:
            parts = token.text_with_ws.split("-")
            word = '-'.join(map(lambda x: x.capitalize(), parts))
            output.append(word)
        else:
            if token.pos_ in CAPS:
                output.append(token.text_with_ws.capitalize())
            else:
                output.append(token.text_with_ws.lower())
    output[0] = output[0].capitalize()
    output[-1] = output[-1].capitalize()
    return "".join(output)

def main():
    logger.info("Read data")
    data = [line.strip() for line in (data_dir / filename).open().readlines()]
    i = 0
    output = []
    logger.info("Start processing")
    for k, line in enumerate(data):
        formatted = format_headline(line)
        if line == formatted:
            i += 1
        if (k+1) % 500 == 0:
            logger.info(f"Processed: {k+1}")
        output.append(f"{formatted}\n")
    logger.info("Write results to the file")
    with (path / output_filename).open("w+") as f:
        f.writelines(output)
    logger.info(f"No. of proper headlines: {i}")
    return 0

if __name__=="__main__":
    code = main()
    sys.exit(code)
