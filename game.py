import json
import random
import pprint
from typing import Iterable


WordWeights = dict[str, float]
LetterProbs = dict[str, float]


def get_letter_prob(word2weight: WordWeights, # Считает проценты без буквы
                    letter: str,
                    ) -> float:
    total_weight = sum(word2weight.values())
    letter_weight = sum(
        weight
        for word, weight in word2weight.items()
        if letter in word
    )
    return letter_weight / total_weight


def remove_containing_letter(word2weight: WordWeights, # Убирает слова с учетом буквы
                             letter: str,
                             ) -> WordWeights:
    return {
        word: weight
        for word, weight in word2weight.items()
        if letter not in word
    }


def get_all_letter_positions(word: str, letter: str) -> tuple[int]: # Получить кортеж позиций буквы в слове
    return tuple(
        idx
        for idx, ch in enumerate(word)
        if ch == letter
    )


def filter_vocabulary_by_mask(word2weight: WordWeights, # Загаданное слово и названия буква -> Новый словарь
                              answer: str,
                              letter: str,
                              ) -> WordWeights:
    answer_pos = get_all_letter_positions(answer, letter)
    return {
        word: weight
        for word, weight in word2weight.items()
        if get_all_letter_positions(word, letter) == answer_pos
    }


def make_move(word2weight: WordWeights, # Сократить словарь с учетом новой буквы
              answer: str,
              picked_letter: str) -> WordWeights:
    if picked_letter in answer:
        return filter_vocabulary_by_mask(word2weight, answer, picked_letter)
    return remove_containing_letter(word2weight, picked_letter)


def analyze_move(word2weight: WordWeights,
                 answer: str,
                 picked_letter: str,
                 possible_letters: Iterable[str],
                 ) -> tuple[WordWeights, LetterProbs]:
    probs = {
        letter: get_letter_prob(word2weight, letter)
        for letter in possible_letters
    }
    new_vocab = make_move(word2weight, answer, picked_letter)
    return new_vocab, probs


def analyze_game(answer: str,
                 picked_letters: Iterable[str],
                 ) -> list[LetterProbs]:
    with open('words.json') as cat_file:
        f = cat_file.read()
    data = json.loads(f)
    word2weight = {}
    for key in data:
        if len(key) == len(answer):
            word2weight[key] = 1.00
    word2weight = {
        word: weight
        for word, weight in word2weight.items()
        if len(word) == len(answer)
    }
    possible_letters = set('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'.lower())
    all_probs = []
    for picked_letter in picked_letters:
        word2weight, probs = analyze_move(
            word2weight,
            answer,
            picked_letter,
            possible_letters,
        )
        all_probs.append(probs)
        possible_letters.remove(picked_letter)
    return all_probs


class Game:
    def __init__(self):
        self.word = ' '
        self.meaning = ' '
        self.live = 6
        self.guessed_letters = ' '
        self.all_letters = ' '
        self.buttons_line = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧЩШЬЫЪЭЮЯ'
        self.use_clue = '111'

    def encode(self):
        string = ''
        for elem in self.guessed_letters:
            string += elem
        string2 = ''
        for elem in self.all_letters:
            string2 += elem
        return '---'.join([self.word, self.meaning, str(self.live), string, string2, self.use_clue])

    def decode(self, string):
        self.word, self.meaning, self.live, self.guessed_letters, self.all_letters, self.use_clue = string.split('---')
        self.live = int(self.live)

    def get_string(self):
        answer = ''
        for elem in self.word:
            if elem in self.guessed_letters:
                answer += elem
            else:
                answer += '-'
        return answer

    def get_buttons_line(self):
        string = ''
        for elem in self.buttons_line:
            if elem.lower() in self.all_letters:
                string += ' '
            else:
                string += elem
        return string

    def generate_word(self):
        with open('words.json') as cat_file:
            f = cat_file.read()
            data = json.loads(f)
            key = random.choice(list(data.items()))
        self.word = ''
        for elem in key[0]:
            if elem == 'ё':
                self.word += 'е'
            elif elem == '-':
                self.generate_word()
            else:
                self.word += elem
        self.word = key[0]
        self.meaning = key[1]['definition']
        self.guessed_letters += self.word[0]
        self.buttons_line = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧЩШЬЫЪЭЮЯ'
        self.all_letters += self.word[0]
        self.live = 6

    def use_letter(self, letter):
        if letter in self.word:
            self.guessed_letters += letter
        else:
            self.live -= 1

    def delete_letters(self):
        string = ''
        while len(string) < 3:
            a = random.choice(self.buttons_line).lower()
            if a not in self.word and a not in string:
                string += a
        for elem in string:
            self.all_letters += elem

    def get_letter(self):
        a = random.choice(self.word)
        if a not in self.guessed_letters:
            self.guessed_letters += a
            self.all_letters += a
        else:
            self.get_letter()

    def get_meaning(self):
        return self.meaning


if __name__ == '__main__':
    pprint.pprint(analyze_game('акр', 'иапк'))
