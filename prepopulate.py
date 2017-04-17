import os
import sys
import io


def populate():
  # Build dictionary mapping each user to their information
  all_users_info_location = "scripts/data_retrieval/all_users_info"
  user_to_info_dict = {}
  with open(all_users_info_location, 'r') as f:
    rows = f.read().split("\n")[:-1]  # ignore last empty line
    for row in rows:
      user_info = row.split(",")
      if user_info[0] != "handle":
        user_to_info_dict[unicode(user_info[1])] = user_info

  # Populate database with the tag objects
  tags = [u'liberal', u'food_lover', u'music_lover', u'art_lover', u'science_lover', u'gamer', u'sports_fan', \
             u'fashion_lover', u'conservative', u'religious']
  for tag in tags:
    Tag.objects.get_or_create(name=tag)


  # Create a TwitterUser object for each tagged user, as well as creating the objects that associate tags to users
  location = "scripts/machine_learning/trained_naive_bayes_model/user_tags.txt"
  with io.open(location, 'r', encoding="ISO-8859-1") as f:
    # test = "Sanders: democrat\nTrump: republican\nObama: democrat"
    rows = f.read().split("\n")[:-1] #ignore last empty line
    for row in rows:
      try:
        items = row.split(": ")
        name = items[0].encode('utf-8')
        print name
        user_info = user_to_info_dict[name]
        twitter_user = TwitterUser.objects.get_or_create(
            twitter_handle=unicode(user_info[0]),
            name=unicode(user_info[1]),
            profile_image=user_info[2]
        )[0]
        tags = items[1].split(" ")
        for tag in tags:
          if tag:
            tag = unicode(tag).strip()
            tag_obj = Tag.objects.get(name=unicode(tag))
            UserTag.objects.get_or_create(
              tag=tag_obj,
              user=twitter_user
            )
      except Exception as e:
        print "Could not be added to the database: " + str(row)


# Start execution here!
if __name__ == '__main__':
  reload(sys)
  sys.setdefaultencoding("utf-8")
  print "Starting prepopulation script..."
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.localsettings')

  import django
  django.setup()

  from project_template.models import UserTag, TwitterUser, Tag
  populate()
