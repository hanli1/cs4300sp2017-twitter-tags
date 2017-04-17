from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import loader
from .form import QueryForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import simplejson as json
from django.http import JsonResponse
import os
import numpy as np
from .models import UserTag, TwitterUser, Tag

from cos_sim import setup_and_run


# Create your views here.
def index(request):
  output=''
  if request.GET.get('search'):
    search = request.GET.get('user_query')
    tags = request.GET.getlist('tags[]')
    print search
    print tags
    # do operations here
    # output = "HELLO"
    paginator = Paginator([], 10)
    page = request.GET.get('page')
    try:
      output = paginator.page(page)
    except PageNotAnInteger:
      output = paginator.page(1)
    except EmptyPage:
      output = paginator.page(paginator.num_pages)
  return render_to_response('project_template/index.html', 
             {'output': output,
              'magic_url': request.get_full_path(),
              })


def search(request):
  search = request.GET.get('user_query')
  tags = request.GET.getlist('tags[]')
  space_index = search.index(" ")
  name = search[space_index + 1:]
  cossim = setup_and_run(name)
  if tags:
    first_tag_tuples= list(UserTag.objects.filter(category=tags[0]).values("name"))
    first_tag_people = set([i["name"] for i in first_tag_tuples])
    set_of_users = first_tag_people
    tags = tags[1:]
    for tag in tags:
      tuples= list(UserTag.objects.filter(category=tag).values("name"))
      people = set([i["name"] for i in tuples])
      set_of_users = set_of_users.intersection(people)
    results = [i for i in cossim if i[0] in set_of_users][:10]
  else:
    results = cossim[:10]
  data = {}
  data["results"] = results
  return JsonResponse(data)


def get_users_handles(request):
  user_tags = TwitterUser.objects.all()
  users = []
  for user_tag in user_tags:
    user = user_tag.user
    users.append({"value": user.twitter_handle + " " + user.name})
  data = {"suggestions": users}
  return JsonResponse(data)


def get_tag_labels(request):
  og_tags = [u'liberal', u'food_lover', u'music_lover', u'art_lover', u'science_lover', u'gamer', u'sports_fan', \
             u'fashion_lover', u'conservative', u'religious']
  tags = [{"value": i} for i in og_tags]

  data = {"suggestions": tags}
  return JsonResponse(data)


def get_user_info(request):
  twitter_handle = request.GET.get("twitter_handle")
  try:
    user = TwitterUser.objects.get(twitter_handle=twitter_handle)
    user_tags_objects = UserTag.objects.filter(user=user)
    user_tags_list = []
    for tag_obj in user_tags_objects:
      user_tags_list.append(tag_obj.name)
    return {
      "user_data": {
        "name": user.name,
        "twitter_handle": user.twitter_handle,
        "profile_image": user.profile_image
      },
      "user_tags": user_tags_list
    }
  except Exception as e:
    return {
      "user_data": {
        "name": "User Not Found",
        "twitter_handle": "",
        "profile_image": "http://placehold.it/250x250"
      },
      "user_tags": []
    }
