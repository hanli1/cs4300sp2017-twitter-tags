import time
import signal
from msvcrt import getch
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome('C:\Users\Han\Downloads\chromedriver.exe')

count = 0
handles = []
followers = "3882082"
try:

  while len(handles) < 1000:
    browser.get("https://moz.com/followerwonk/bio/?q_type=all&frmin=0&frmax=0&flmin=0&flmax=" + followers + "&stctmin=0&stctmax=0")
    # time.sleep(10)

    elem = browser.find_element_by_tag_name("body")
    handles_obj = browser.find_elements_by_class_name("person_scrn")
    for h in handles_obj:
      if h.text not in handles:
        handles.append(h.text)

    followers = browser.find_elements_by_class_name("a_r")
    followers = (followers[::3][-1]).text.replace(",", "")
finally:
  with open("new_users_handles.txt", "a+") as f:
    for h in handles:
      f.write(h + "\n")

