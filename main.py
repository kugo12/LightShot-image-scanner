print("1.0.0")

import lxml
import requests
from bs4 import BeautifulSoup
import keyboard
import threading
import sys
import os


# --- config
prefix = 'rohe'  # should be 6 chars long max
break_key = "x"  # breaks from scanning and downloading loops


# --- vars
key_pressed = False
def on_x_pressed():
    global key_pressed
    while True:
        if keyboard.read_key() == break_key:
            key_pressed = True

id = ''
url = 'https://prnt.sc/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}


# --- getting combinations
charset = 'abcdefghijklmnopqrstuvwxyz0123456789'  # abcdefghijklmnopqrstuvwxyz0123456789
combinations = []
repeat = (6 - len(prefix)) - 1
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
    os.system("pause")



# --- starting thread for breaking from the loops
key_thread = threading.Thread(target=on_x_pressed)
key_thread.daemon = True
key_thread.start()


# --- scanning sites
id_list = []
counter = 0
c_max = len(combinations)
percent_new = round(counter * 100 / c_max)
percent_old = -1
for suffix in combinations:

    if key_pressed:
        key_pressed = False
        break

    id = prefix + suffix
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

        if key_pressed:
            download_interrupted = True
            break

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
os.system("pause")