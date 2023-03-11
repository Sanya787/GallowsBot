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

    def encode(self):
        string = ''
        for elem in self.guessed_letters:
            string += elem
        string2 = ''
        for elem in self.all_letters:
            string2 += elem
        return '---'.join([self.word, self.meaning, str(self.live), string, string2])

    def decode(self, string):
        self.word, self.meaning, self.live, self.guessed_letters, self.all_letters = string.split('---')
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

    def get_meaning(self):
        return self.meaning
