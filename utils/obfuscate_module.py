import requests
from random import choice

key = "6da60020-3dd2-4eda-8bd2-15fbe20c0678"


def get_synonyms(word: str):
    blacklisted_words = ["the", "a", "is", "my"]

    if word.lower() in blacklisted_words:
        return []

    request_string = f"https://dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={key}"
    result = requests.get(request_string)
    output = result.json()

    synonyms = []
    try:
        if output:
            synonyms = output[0]["meta"]["syns"][0]
    except TypeError:
        # if this happens, we got a bad response and should just skip this word.
        pass

    return synonyms


def obfuscate(phrase: str):
    words = phrase.split()
    count = 0

    for word in words:
        synonyms = get_synonyms(word)
        if synonyms:
            words[count] = choice(synonyms)

        count += 1

    output = " ".join(words)
    return output
