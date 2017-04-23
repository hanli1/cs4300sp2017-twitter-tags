import time
import signal
from msvcrt import getch
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome('C:\Users\Han\Downloads\chromedriver.exe')

browser.get("https://moz.com/followerwonk/bio/?q_type=all&frmin=0&frmax=0&flmin=0&flmax=4000000&stctmin=0&stctmax=0")
time.sleep(10)

elem = browser.find_element_by_tag_name("body")

done = False

handles = browser.find_elements_by_class_name("person_scrn")
for h in handles:
  print h.text

    # post_elems = browser.find_elements_by_class_name("more_link")
    # file = open("data.txt", "w")
    # for post in post_elems:
    #   file.write(post.get_attribute("href") + "\n") 
