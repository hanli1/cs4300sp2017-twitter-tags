import os
import sys
import io
import mimetypes, urllib2

def is_url_image(url):
    mimetype,encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))

def check_url(url):
    """Returns True if the url returns a response code between 200-300,
       otherwise return False.
    """
    try:
        headers={
            "Range": "bytes=0-10",
            "User-Agent": "MyTestAgent",
            "Accept":"*/*"
        }

        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        return response.code in range(200, 209)
    except Exception, ex:
        return False

def is_image_and_ready(url):
    return (is_url_image(url) and check_url(url))


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

  people_users = set()
  # Fetch all people users
  with io.open("scripts/data_retrieval/people_users.txt", 'r', encoding="ISO-8859-1") as f:
    rows = f.read().split("\n")[:-1]
    for row in rows:
      people_users.add(unicode(row.strip()))

  # Populate database with the tag objects
  tags = [u'liberal', u'food_lover', u'music_lover', u'art_lover', u'science_lover', u'gamer', u'sports_fan', \
             u'fashion_lover', u'conservative', u'religious']
  for tag in tags:
    Tag.objects.get_or_create(name=tag)

  #remove all existing users
  TwitterUser.objects.all().delete()

  # Create a TwitterUser object for each tagged user, as well as creating the objects that associate tags to users
  location = "scripts/machine_learning/trained_naive_bayes_model/user_tags_v4.txt"
  with io.open(location, 'r', encoding="ISO-8859-1") as f:
    # test = "Sanders: democrat\nTrump: republican\nObama: democrat"
    rows = f.read().split("\n")[:-1] #ignore last empty line
    for row in rows:
      try:
        items = row.split(": ")
        name = items[0].encode('utf-8')
        user_info = user_to_info_dict[name]
        user_info[2] = user_info[2].strip()
        high_res = user_info[2].replace("_normal", "")
        if is_image_and_ready(high_res):
          user_info[2] = high_res

        if unicode(user_info[1]) in people_users:
          twitter_user = TwitterUser.objects.get_or_create(
              twitter_handle=unicode(user_info[0]),
              name=unicode(user_info[1]),
              profile_image=user_info[2],
              user_type="person"
          )[0]
        else:
          twitter_user = TwitterUser.objects.get_or_create(
            twitter_handle=unicode(user_info[0]),
            name=unicode(user_info[1]),
            profile_image=user_info[2],
            user_type="organization"
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
