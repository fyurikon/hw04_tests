from django import forms

import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher
import pymorphy2
from typing import List, Tuple

from .models import Post, CensoredWord

nltk.download('punkt')

similarity_threshhold: float = 0.8


def join_punctuation(seq: List[str], characters: str = '.,;?!') -> str:
    """Combine words and characters into string."""
    characters = set(characters)
    seq = iter(seq)
    current = next(seq)

    for nxt in seq:
        if nxt in characters:
            current += nxt
        else:
            yield current
            current = nxt

    yield current


def lemmatize_words(tokenized_words: List[str]) -> List[str]:
    """Lemmatize words."""
    morph = pymorphy2.MorphAnalyzer()
    result = [morph.parse(word)[0].normal_form for word in tokenized_words]

    return result


def stemmatize_words(tokenized_words: List[str]) -> List[str]:
    """Stemmatize words."""
    snowball = SnowballStemmer("russian")
    result = [snowball.stem(word) for word in tokenized_words]

    return result


def bad_language_validation(text: str, stop_words: List[str],
                            similarity_threshold: float) -> Tuple[str, bool]:
    """Check if text contains bad words and replace it with asterisks."""
    bad_words_idx: int = []
    validation_error: bool = False
    tokenized_words: List[str] = word_tokenize(text)

    lemmed_words: List[str] = lemmatize_words(tokenized_words)
    lemmed_stop_words: List[str] = lemmatize_words(stop_words)

    stemmed_stop_words: List[str] = stemmatize_words(lemmed_stop_words)
    stemmed_words: List[str] = stemmatize_words(lemmed_words)

    for i in range(len(stemmed_words)):
        if stemmed_words[i] in stemmed_stop_words:
            bad_words_idx.append(i)
            validation_error = True
            continue

        for stop_word in stemmed_stop_words:
            s = SequenceMatcher(None, stop_word, stemmed_words[i])
            if s.quick_ratio() > similarity_threshold:
                bad_words_idx.append(i)
                validation_error = True

    bad_words_idx = set(bad_words_idx)

    for i in bad_words_idx:
        tokenized_words[i] = '*' * len(tokenized_words[i])

    result: str = ' '.join(join_punctuation(tokenized_words))

    return result, validation_error


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ('text', 'group')

    def clean_text(self):
        text: str = self.cleaned_data['text']
        stop_words = CensoredWord.objects.values_list('word', flat=True)

        data: Tuple[str, bool] = bad_language_validation(
            text,
            stop_words,
            similarity_threshhold
        )

        text = data[0]
        validation_error = data[1]

        if validation_error:
            raise forms.ValidationError(
                ('Пожалуйста, исправьте слова, что '
                 'отмечены звёздочками: %(value)s'),
                code='invalid',
                params={'value': text})

        return text
