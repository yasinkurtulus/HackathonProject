from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Modeli ve tokenizer'ı yükle
model_name = "ckartal/english-to-turkish-finetuned-model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
translator = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def translate_tur(sentence):
    inputs = tokenizer(sentence, return_tensors="pt")

    # Çeviri üret
    outputs = translator.generate(
        **inputs,
        max_length=100,  # çıktı uzunluğu
        num_beams=4,  # beam search ile daha iyi sonuç
        early_stopping=True
    )
    turkish = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return turkish


