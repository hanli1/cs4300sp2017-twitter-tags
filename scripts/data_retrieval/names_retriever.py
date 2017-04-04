import requests
import sys
from bs4 import BeautifulSoup
import time


#Returns twitter handle of top # users based on number of followers 
top_num = int(sys.argv[1]);

start_time = time.time()
if (top_num > 900 or top_num < 100 or top_num%100 != 0):
  print("Invalid Number")

names = []
num = 0
for _ in range(0, top_num/100):
  if num == 0:
    url = 'http://twittercounter.com/pages/100/'
  else:
    url = 'http://twittercounter.com/pages/100/' + str(num)

  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  names += [s.text for s in soup.findAll('span', itemprop='name')]
  num += 100

writer  = open('top_users_name.txt', 'w')
for n in names[3:]:
  writer.write(n.encode("utf-8") + "\n");
writer.close() 

print("--- %s seconds ---" % (time.time() - start_time))