from nltk.stem import PorterStemmer, LancasterStemmer
from nltk.corpus import words # Import words here
import nltk
from nltk.corpus import wordnet as wn
nltk.download('words') # Ensure words is downloaded here
import analyzer, translate
import google.generativeai as genai
import os,api_k
genai.configure(api_key=api_k.api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

english_words = set(words.words())

def is_english_word(word):
    porter = PorterStemmer()
    return bool(wn.synsets(word)or(wn.synsets(porter.stem(word))))

def construct_word(text,sentence):
  #check it is an english word or not
  try:
      print(f"Checking if '{text}' is English word...")
      if not(is_english_word(text)):
          print(f"{text} is not an english word")
          return text.lower(), "noun"  # fallback
      else:
        print(f"Analyzing word '{text}' in sentence...")
        word_features=analyzer.analyze_word_in_sentence(text,sentence)
        print(f"Word features: {word_features}")
        if isinstance(word_features, dict) and 'error' in word_features:
            # Fail fast so upper layers can inform the user
            raise ValueError(word_features['error'])
        lemma,tag=(word_features["lemma"],word_features["pos"])
        return lemma.lower(),tag.lower()
  except Exception as e:
      print(f"Error in construct_word: {e}")
      # Propagate the error so API layer can return an error to user
      raise


def generate_sentences(word,sample_sentence, tenses,interests):
    """
    Tek bir prompt ile verilen kelime için tüm zamanlarda örnek cümleler üretir.
    """
    try:
        print(f"Starting generate_sentences with word: {word}, sample: {sample_sentence}")
        level="b1"
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        lemma,tag=construct_word(word,sample_sentence)
        print(f"Constructed word - lemma: {lemma}, tag: {tag}")
        tense_list = ", ".join(tenses)
        #Liste olan ilgi alanlarını birleştirip stringe çeviriyoruz. böylece propmta girebilelim.
        interests_list = ", ".join(interests)
        print(f"Interests list: {interests_list}")
    except Exception as e:
        print(f"Error in generate_sentences setup: {e}")
        raise

    info_prompt = (
    f"Explain the English word '{lemma}' only in its role as a {tag}. "
    f"Provide a short and clear English definition (one sentence). "
    f"Do not include other possible parts of speech or meanings. "
    f"Format: 'Definition: ...'"
    )


    try:
        info_resp = model.generate_content(info_prompt)
        word_info = info_resp.text.strip()
    except Exception as e:
        word_info = f"Could not retrieve info: {e}"
    #Promptan definiton: kısmını silmek istiyorum
    clean_eng = word_info.replace("Definition:", "", 1).strip()
    turkish_inf=translate.translate_tur(clean_eng)
    # Return lemma so UI can display the root form (e.g., balls -> ball)
    info={"eng":clean_eng,"tur":turkish_inf,"type":tag, "lemma": lemma}


    if tag=="verb":
        prompt = (
              f"Generate exactly one English sentence for each of the following tenses: {tense_list}. "
              f"Use the word '{lemma}' in each sentence as a {tag}. "
              f"Vary the context and keep the grammar and vocabulary appropriate for {level} level. "
              f"If the word is a verb, conjugate it correctly for the specified tense. "
              f"If it is a noun, adjective, or adverb, use it naturally in the sentence in that role. "
              f"For each sentence, explicitly choose a different theme from this list of interests: {interests_list}. "
              f"Provide only the sentences, one per line, in the same order as the tenses."
              )

        try:
          response = model.generate_content(prompt)
          lines = [ln.strip() for ln in response.text.split("\n") if ln.strip()]
          generated_sentences = []
          for tense, sentence in zip(tenses, lines):
                turkish=translate.translate_tur(sentence)
                generated_sentences.append({"tense": tense, "sentence": sentence,"turkish":turkish})
        except Exception as e:
          print(f"Error generating sentences: {e}")
          generated_sentences = [
              {"tense": tense, "sentence": f"Error generating sentence: {e}"} for tense in tenses
          ]
    else:
        k = 5  # kaç örnek istiyorsan
        prompt = (
              f"Generate {k} different English sentences suitable for a {level} learner of English. "
              f"Each sentence must use the word '{lemma}' as a {tag}. "
              f"Vary the context and keep the grammar and vocabulary appropriate for {level} level. "
              f"For each of the {k} sentences, use a different theme from this list of interests: {interests_list}. "
              f"Do not repeat the same interest twice. "
              f"Provide only the sentences, one per line."
              )


        try:
            response = model.generate_content(prompt)
            lines = [ln.strip() for ln in (response.text or "").split("\n") if ln.strip()]
            # fazlaysa kırp, eksikse olduğu kadarını al
            lines = lines[:k]

            generated_sentences = []
            for i, sentence in enumerate(lines, start=1):
                turkish=translate.translate_tur(sentence)
                generated_sentences.append({"example": i, "sentence": sentence,"turkish":turkish})

        except Exception as e:
            print(f"Error generating sentences: {e}")
            generated_sentences = [{"example": i + 1, "sentence": f"Error: {e}"} for i in range(k)]

    return info,generated_sentences


