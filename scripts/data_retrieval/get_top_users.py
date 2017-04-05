import requests
import sys
from bs4 import BeautifulSoup
import time


#Returns twitter handle of top # users based on number of followers
top_num = int(sys.argv[1]);

start_time = time.time()
if (top_num > 1000 or top_num < 100 or top_num%100 != 0):
  print("Invalid Number")

names = []
num = 0
for _ in range(0, top_num/100):
  # url = 'http://twitaholic.com/top' + str(num) + '/followers/'
  if num == 0:
    url = 'http://twittercounter.com/pages/100/'
  else:
    url = 'http://twittercounter.com/pages/100/' + str(num)

  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  # names += [s.text for s in soup.findAll('td', class_='statcol_name')]
  names += [s.text for s in soup.findAll('span', itemprop='alternateName')]
  num += 100

writer  = open('top_users_handle.txt', 'w')
for n in names:
  # handle = n[n.find('@'):]
  # writer.write(handle)
  writer.write(n + "\n");
writer.clos
print("--- %s seconds ---" % (time.time() - start_time))

