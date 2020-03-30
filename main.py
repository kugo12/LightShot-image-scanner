import requests
from bs4 import BeautifulSoup
import sys
import os
import configparser
import signal


# --- setup
if not os.path.isdir('data'):
    os.mkdir('data')
if not os.path.isfile('scanned_IDs.txt'):
    open('scanned_IDs.txt', 'x')

def break_signal_handler(signal, frame):
    try:
        print('\nCtrl-c break')
    except RuntimeError:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, break_signal_handler)


# --- config
class Config(configparser.ConfigParser):
    defaults = {
        'prefix': 'rohee', 
    }
    config_fn = 'config.ini'

    # placeholder for vars
    prefix: str

    def __init__(self):
        super().__init__()
        self.read(self.config_fn)

        for i in self.defaults:
            # set variables
            setattr(self, i, self.get('main', i, fallback=self.defaults[i]))

        # if config file is not existing create it
        if not os.path.isfile(self.config_fn):
            self.write()

    def write(self):
        # set values to write
        self.add_section('main')
        for i in self.defaults:
            self.set('main', i, self.defaults[i])

        with open(self.config_fn, 'w') as f:
            super().write(f)



# --- vars
cfg = Config()
id = ''
url = 'https://prnt.sc/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}



# --- getting combinations
charset = 'abcdefghijklmnopqrstuvwxyz0123456789'  # abcdefghijklmnopqrstuvwxyz0123456789
combinations = []
repeat = (6 - len(cfg.prefix)) - 1
x = [char for char in charset]
for loop in range(repeat):
    x = [y + char for char in charset for y in x]
combinations += x

try:
    scanned_IDs = []
    with open('scanned_IDs.txt', 'r+') as f_scanned_IDs:
        for line in f_scanned_IDs:
            line = str(line).replace("\n", "")
            scanned_IDs.append(line)
except FileNotFoundError:
    print("Couldn't find \"scanned_IDs.txt\" file!")
    sys.exit(1)



# --- scanning sites
id_list = []
counter = 0
c_max = len(combinations)
percent_new = round(counter * 100 / c_max)
percent_old = -1
for suffix in combinations:

    id = cfg.prefix + suffix
    if id not in scanned_IDs:

        percent_new = round(counter * 100 / c_max)
        if percent_new != percent_old:
            print(f'Searching for images: {percent_new}%')
            percent_old = percent_new

        _url = url + id
        result = requests.get(_url, headers=headers)
        src = result.content
        soup = BeautifulSoup(src, features='lxml')

        data = soup.find_all("img", {"class": "no-click screenshot-image"})
        for x in data:
            _src = x.get('src')
            _id = x.get('image-id')
            scanned_IDs.append(str(_id))

            # ignore "not found" images
            if not "imageshack.us" in _src and not _src.startswith('//st.prntscr.com/2020/03/13/0139/img/0_173a7b_211be8ff.png'):
                id_list.append([_id, _src])
        counter += 1
print(f'Searching for images: 100%')


# --- downloading images
error_msg = "Downloading stopped by user."
c_max = len(id_list)
counter = 0
download_interrupted = False
downloaded_images = []
percent_old = -1
try:
    for x in id_list:
        percent_new = round(counter * 100 / c_max)
        if percent_new != percent_old:
            print(f'Downloading images: {percent_new}%')
            percent_old = percent_new

        f = open(f'data/{x[0]}.png', 'xb')
        f.write(requests.get(x[1]).content)
        f.close()

        downloaded_images.append(x[0])
        counter += 1
except:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    error_msg = f"ERROR [{exc_type}] in [{fname}] at [{exc_tb.tb_lineno}] \n{exc_obj}"
    download_interrupted = True

if download_interrupted:
    print(f"Download has been interrupted\n{error_msg}")

    tmp_list = []
    for id_ in scanned_IDs:
        if id_ in downloaded_images:
            tmp_list.append(id_)
    scanned_IDs = tmp_list


# --- saving data about downloaded images
with open('scanned_IDs.txt', 'a') as f_scanned_IDs:
    for scanned_site in scanned_IDs:
        f_scanned_IDs.write(f'{scanned_site}\n')


# --- ending
print("DONE!")
sys.exit(0)