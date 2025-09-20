import nltk

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, words as nltk_words
from nltk import pos_tag, word_tokenize
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
nltk.download('averaged_perceptron_tagger_eng')
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
# Add this line to download the required resource
nltk.download('punkt')
nltk.download('punkt_tab')

#Bu modül verilen kelimenin türünü (sıfat ,isim, fiil vb.) analiz eder



def simplify_pos(tag: str) -> str:
    if tag.startswith('V'): return 'verb'
    if tag.startswith('J'): return 'adj'
    if tag.startswith('N'): return 'noun'
    if tag.startswith('R'): return 'adv'
    return 'other'

WN_POS_MAP = {
    'N': wordnet.NOUN,
    'V': wordnet.VERB,
    'J': wordnet.ADJ,
    'R': wordnet.ADV
}

def to_wordnet_pos(tag: str):
    return WN_POS_MAP.get(tag[0], None)

MODALS = {"will","shall","can","could","may","might","must","should","would"}
AUX_DO = {"do","does","did"}
TO = {"to"}

SUBJECT_PRONOUNS = {"i","you","we","they","he","she"}

def refine_tags(tokens, tagged):
    """
    Basit bağlam kurallarıyla POS düzeltmeleri.
    - Modal/TO/Aux-do sonrası kelime -> VB
    - PRP (özne) + NN + (DT/PRP$/JJ/NN) -> orta öğe muhtemelen fiil (VB)
    - VBN + NOUN -> ilkini JJ yap (participle as adjective)
    """
    refined = list(tagged)

    for i, (tok, tag) in enumerate(tagged):
        prev_tok = tokens[i-1].lower() if i-1 >= 0 else ""
        prev_tag = tagged[i-1][1] if i-1 >= 0 else ""
        next_tag = tagged[i+1][1] if i+1 < len(tagged) else ""
        next_tok = tokens[i+1].lower() if i+1 < len(tagged) else ""

        # 1) noun etiketlenmiş ama modal/TO/Aux-do sonrası: muhtemelen fiil (VB)
        if tag.startswith("N"):
            if prev_tok in MODALS or prev_tok in TO or prev_tok in AUX_DO:
                refined[i] = (tok, "VB")
                continue

            # 2) Özne zamirinden sonra 'NN' ve ardından bir isim öbeği başlatıcı geliyorsa -> VB
            if (prev_tag == "PRP" or prev_tok in SUBJECT_PRONOUNS):
                if next_tag.startswith(("DT", "JJ", "NN")) or next_tok in {"a","an","the"}:
                    refined[i] = (tok, "VB")
                    continue

        # 3) VBN + NOUN dizilimi: çoğu zaman JJ + NOUN (örn. taken house)
        if tag == "VBN" and next_tag.startswith("N"):
            refined[i] = (tok, "JJ")
            continue

    return refined


def analyze_word_in_sentence(word: str, sentence: str):
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)

    # refine
    tagged = refine_tags(tokens, tagged)

    # hedef kelimeyi bul
    target_lower = word.lower()
    match_idx = None
    for i, tok in enumerate(tokens):
        if tok.lower() == target_lower:
            match_idx = i
            break
    if match_idx is None:
        stripped = ''.join(ch for ch in target_lower if ch.isalnum())
        for i, tok in enumerate(tokens):
            if ''.join(ch for ch in tok.lower() if ch.isalnum()) == stripped:
                match_idx = i
                break
    if match_idx is None:
        return {"error": f"Kelime cümlede bulunamadı: '{word}'",
                "tokens": tokens, "tagged": tagged}

    tok, tag = tagged[match_idx]
    simple = simplify_pos(tag)

    # Lemma
    wnl = WordNetLemmatizer()
    wn_pos = to_wordnet_pos(tag)
    if wn_pos:
        lemma = wnl.lemmatize(tok, pos=wn_pos)
    else:
        lemma = wnl.lemmatize(tok)

    return {
        "token": tok,
        "index": match_idx,
        "pos_tag": tag,
        "pos": simple,
        "lemma": lemma
    }