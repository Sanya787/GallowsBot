import json
import random


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
        self.all_letters = ' '
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
