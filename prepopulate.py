import os
import sys
import io
reload(sys)
sys.setdefaultencoding("utf-8")

def populate():
  location = "scripts\\machine_learning\\trained_naive_bayes_model\\user_tags.txt"
  with io.open(location, 'r', encoding="ISO-8859-1") as f:
    # test = "Sanders: democrat\nTrump: republican\nObama: democrat"
    rows = f.read().split("\n")[:-1] #ignore last empty line
    for row in rows:
      items = row.split(": ")
      name = items[0]
      tags = items[1].split(" ")
      for tag in tags:
        if tag:
          p = UserTag.objects.get_or_create(name=unicode(name), category=tag)[0]
          # print "added: " + str(p)

  

# Start execution here!
if __name__ == '__main__':
  print "Starting prepopulation script..."
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

  import django
  django.setup()

  from project_template.models import UserTag
  #purge db
  UserTag.objects.all().delete()
  populate() 

  #retrieve some stuff
  # cat = list(UserTag.objects.filter(category="fashion_lover").values("name"))
  # cat = [i["name"] for i in cat]
  cat = list(UserTag.objects.all().values("category"))
  cat = set([i["category"] for i in cat])
  print cat  