import numpy as np
import cv2

from GUIlib import WindowGUI


class App(WindowGUI):
    def __init__(self):
        super().__init__()
        self.win_h = 260
        self.win_w = 175
        self.name = 'Calc Pro'
        self.expression = ''

    def __call__(self, img, fingers_up, fingers_touch, landmark, buffer: list):
        super().__call__(img, fingers_up, fingers_touch, landmark, buffer)
        if self.hide:
            return

        self.rectangle(img, 0, 0, self.win_w, 40, (255, 255, 255))
        self.text(img, 10, 30, self.expression, (0, 0, 0))

        keys = [
            'c()/',
            '789*',
            '456-',
            '123+',
            '<0.=',
                ]

        for y, row in enumerate(keys):
            for x, c in enumerate(row):
                self.button(img, x * 45, 40 + y * 45, 40, 40, c, (0, 0, 230),
                            lambda k=c: self.calc(k), fingers_touch, landmark)

    def calc(self, x):
        if x == 'c':
            self.expression = ''
        elif x == '<':
            self.expression = self.expression[:-1]
        elif x == '=':
            try:
                self.expression = str(eval(self.expression))
            except SyntaxError:
                pass
            except ZeroDivisionError:
                pass
        else:
            self.expression += x
