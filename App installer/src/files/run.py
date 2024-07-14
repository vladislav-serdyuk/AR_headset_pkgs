"""
Copyright (C) 2024  Vladislav Serdyuk

Этот файл — часть AR_headset.
AR_headset — свободная программа: вы можете перераспространять ее и/или
изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
в каком она была опубликована Фондом свободного программного обеспечения;
либо версии 3 лицензии, либо любой более поздней версии.
AR_headset распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ;
даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ.
Подробнее см. в Стандартной общественной лицензии GNU.
Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой.
Если это не так, см. <https://www.gnu.org/licenses/>.
"""

from json import JSONDecoder
import base64
import wget
import threading
import random

from GUIlib import WindowGUI
import pkgmgr
import os

from github import Github
from github.GithubException import UnknownObjectException

json_decoder = JSONDecoder()


def get_pkg_list():
    pkg_list = []
    with Github() as gh:
        repo = gh.get_repo('vladislav-serdyuk/AR_headset_pkgs')
        contents = repo.get_contents('')
        for file_content in contents:
            if file_content.type == 'file':
                continue
            # zip_file = None
            for pkg_file_content in repo.get_contents(file_content.path):
                if pkg_file_content.path.endswith('.zip'):
                    zip_file = pkg_file_content
                    break
            else:
                continue
            try:
                pkg_data_file = repo.get_contents(file_content.path + '/src/pkg_data.json')
            except UnknownObjectException:
                continue
            pkg_data_content = base64.b64decode(pkg_data_file.content.encode()).decode()
            pkg_data = json_decoder.decode(pkg_data_content)
            pkg = {'name': pkg_data['info'], 'description': pkg_data['description'], 'dir_on_github': file_content.path,
                   'zip_file': zip_file.path, 'download_size': zip_file.size, 'install_size': None}
            pkg_list.append(pkg)
    return pkg_list


def convert_to_kb_mb_gb(num, _round):
    ed = ['B', 'KB', 'MB', 'GB']
    cnt = 0
    while num >= 1000 and cnt < len(ed):
        num = round(num / 1000, _round)
        cnt += 1
    return f'{num}{ed[cnt]}'


class App(WindowGUI):
    def __init__(self, fingers_up: list[int], fingers_touch: list[int],
                 buffer: list[str], message: list[str], landmark: list[list[int]]):
        super().__init__(fingers_up, fingers_touch, buffer, message, landmark)
        self.name = 'App installer'  # имя окна
        self.windows_height = 300  # высота окна
        self.window_width = 460  # ширина окна
        self.x = 200  # координаты нижнего левого угла
        self.y = 400
        self.pkg_list = None
        self.cur_pkg = None
        self.install_status = ''

    def __call__(self, img):
        super().__call__(img)  # прорисовка и обработка окна
        if self.hide:
            return
        if self.pkg_list is not None:
            for i, item in enumerate(self.pkg_list):
                self.button(img, 5, i * 45 + 5, 200, 40, item['name'], (220, 255, 0),
                            lambda: self.select(item))
        self.button(img, 5, self.windows_height - 45, 200, 40, 'refresh', (200, 200, 200), self.refresh)

        if self.cur_pkg is not None:
            self.text(img, 240, 35, self.cur_pkg['name'], (0, 0, 0))

            self.text(img, 220, 70, 'Information:', (0, 0, 0))
            description_word = self.cur_pkg['description'].split()
            line = ''
            line_num = 0
            for word in description_word:
                if len(line) + len(word) < 18 or (line == '' and len(word) >= 18):
                    line += word + ' '
                else:
                    self.text(img, 220, 110 + line_num * 30, line, (0, 0, 0))
                    line = ''
                    line_num += 1
            self.text(img, 220, 110 + line_num * 30, line, (0, 0, 0))
            self.text(img, 215, self.windows_height - 60, f'download size: {self.cur_pkg["download_size"]}',
                      (0, 0, 0))
            if self.install_status == '':
                self.button(img, 215, self.windows_height - 45, 240, 40, 'Install', (0, 255, 0), self.start_install_pkg)
            else:
                self.text(img, 220, self.windows_height - 20, self.install_status, (0, 0, 255))

    def select(self, pkg):
        self.cur_pkg = pkg

    def refresh(self):
        self.pkg_list = get_pkg_list()
        # self.pkg_list = [{'name': 'Calc Pro', 'description': 'Improved version of the calculator',
        #                   'dir_on_github': 'Calc Pro', 'zip_file': 'Calc Pro/Calc Pro.zip', 'download_size': 123,
        #                   'install_size': -1}]

    def start_install_pkg(self):
        self.install_status = 'preparing to downloading'
        threading.Thread(target=self.install, daemon=True).start()

    def install(self):
        url = f'https://raw.githubusercontent.com/vladislav-serdyuk/AR_headset_pkgs/main/{self.cur_pkg["zip_file"]}'
        # url = f'http://speedtest.ftp.otenet.gr/files/test10Mb.db'
        print(f'downloading {url.replace(" ", "%20")}')
        random_number = random.randint(1, 1_000_000_000)
        wget.download(url, f'pkg_for_install_{random_number}.zip', self.download_tracker)
        self.install_status = 'install'
        print('install pkg')
        pkgmgr.install_pkg(f'pkg_for_install_{random_number}.zip', skip_question=True)
        self.install_status = 'cleanup'
        print(f'deleted pkg_for_install_{random_number}.zip')
        os.remove(f'pkg_for_install_{random_number}.zip')
        self.install_status = ''
        self.send_message('reload-apps')

    def download_tracker(self, current, total, wight):
        self.install_status = \
            f'{round(current / total * 100, 1)}% ({convert_to_kb_mb_gb(current, 1)}/{convert_to_kb_mb_gb(total, 1)})'
