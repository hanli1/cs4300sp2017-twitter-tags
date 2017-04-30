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
  user_type = request.GET.get("user_type")
  space_index = search.rfind(" ")
  name = search[:space_index]
  cossim = setup_and_run(name)
  allowed_users = set()
  if user_type:
    if user_type == "People":
      allowed_users = set(list(TwitterUser.objects.filter(user_type="person")))
    elif user_type == "Organizations":
      allowed_users = set(list(TwitterUser.objects.filter(user_type="organization")))
    else:
      allowed_users = set(TwitterUser.objects.all())
  if tags:
    user_tags= list(UserTag.objects.filter(tag__name=tags[0]))
    first_tag_people = set([user_tag.user.name for user_tag in user_tags])
    set_of_users = first_tag_people
    tags = tags[1:]
    for tag in tags:
      user_tags = list(UserTag.objects.filter(tag__name=tag))
      people = set([user_tag.user.name for user_tag in user_tags])
      set_of_users = set_of_users.intersection(people)
    results = []
    for user_obj in cossim:
      if user_obj["name"] in set_of_users:
        try:
          twitter_user = TwitterUser.objects.get(name=user_obj["name"])
          if len(allowed_users) > 0 and twitter_user in allowed_users:
            results.append({
              "twitter_handle": twitter_user.twitter_handle,
              "profile_picture": twitter_user.profile_image,
              "cosine_similarity": user_obj["cosine_similarity"],
              "name": user_obj["name"],
              "top_words_in_common": user_obj["top_words_in_common"]
            })
            if len(results) >= 10:
              break
        except TwitterUser.DoesNotExist:
          continue
        except Exception as e:
          continue
    results = results[:10]
  else:
    results = []
    for user_obj in cossim:
      try:
        twitter_user = TwitterUser.objects.get(name=user_obj["name"])
        if len(allowed_users) > 0 and twitter_user in allowed_users:
          results.append({
            "twitter_handle": twitter_user.twitter_handle,
            "profile_picture": twitter_user.profile_image,
            "cosine_similarity": user_obj["cosine_similarity"],
            "name": user_obj["name"],
            "top_words_in_common": user_obj["top_words_in_common"]
          })
          if len(results) >= 10:
            break
      except TwitterUser.DoesNotExist:
        continue
      except Exception as e:
        continue
    results = results[:10]
  return JsonResponse({"results": results})


def get_users_handles(request):
  twitter_users = TwitterUser.objects.all()
  users = []
  for twitter_user in twitter_users:
    users.append({"value": twitter_user.name + " (@" + twitter_user.twitter_handle + ")"})
  return JsonResponse({"suggestions": users})


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
      user_tags_list.append(tag_obj.tag.name)
    return JsonResponse({
      "user_data": {
        "name": user.name,
        "twitter_handle": user.twitter_handle,
        "profile_image": user.profile_image
      },
      "user_tags": user_tags_list
    })
  except Exception as e:
    return JsonResponse({
      "user_data": {
        "name": "User Not Found",
        "twitter_handle": "",
        "profile_image": "http://placehold.it/150x150"
      },
      "user_tags": []
    })
