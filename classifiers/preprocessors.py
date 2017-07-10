import re
import pymorphy2


morph = pymorphy2.MorphAnalyzer()


def normalizing_preprocessor(row_string):
    """
    Clears string from everything, except letters
    used in russian or english languages.
    After that, transforms all words to normal form
    """
    cleaned_string = re.sub('[^а-яА-Яa-zA-Z]', ' ', row_string)
    words = cleaned_string.split(' ')
    processed_words = []

    # transform word to normal form
    for word in words:
        word = word.strip()
        # miss words with len < 2
        if len(word) > 1:
            normal_form = morph.parse(word)[0].normal_form

            if not normal_form:
                normal_form = word
            processed_words.append(normal_form)

    processed_string = ' '.join(processed_words)

    return processed_string
