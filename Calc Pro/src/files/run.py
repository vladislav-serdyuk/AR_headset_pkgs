"""
Copyright (C) 2024  Vladislav Serdyuk

Этот файл — часть AR_headset_pkgs.
AR_headset_pkgs — свободная программа: вы можете перераспространять ее и/или
изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
в каком она была опубликована Фондом свободного программного обеспечения;
либо версии 3 лицензии, либо любой более поздней версии.
AR_headset_pkgs распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ;
даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ.
Подробнее см. в Стандартной общественной лицензии GNU.
Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой.
Если это не так, см. <https://www.gnu.org/licenses/>.
"""

import numpy as np
import cv2

from GUIlib import WindowGUI


class App(WindowGUI):
    def __init__(self, fingers_up: list[int], fingers_touch: list[int],
                 buffer: list[str], message: list[str], landmark: list[list[int]]):
        super().__init__(fingers_up, fingers_touch, buffer, message, landmark)
        self.windows_height = 260
        self.window_width = 175
        self.name = 'Calc Pro'
        self.expression = ''

    def __call__(self, img):
        super().__call__(img)
        if self.hide:
            return

        self.rectangle(img, 0, 0, self.window_width, 40, (255, 255, 255))
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
                            lambda k=c: self.calc(k))

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
