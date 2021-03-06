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
  allowed_users = set()
  if user_type:
    if user_type == "People":
      allowed_users = set(list(TwitterUser.objects.filter(user_type="person")))
    elif user_type == "Organizations":
      allowed_users = set(list(TwitterUser.objects.filter(user_type="organization")))
    else:
      allowed_users = set(TwitterUser.objects.all())
  if tags:
    positive_tags = []
    negative_tags = []
    curr_tag = ""
    for i, tag in enumerate(tags):
      if i % 2 == 0:
        curr_tag = tag
      else:
        if tag == "positive":
          positive_tags.append(curr_tag)
        else:
          negative_tags.append(curr_tag)

    set_of_users = set([twitter_user.name for twitter_user in TwitterUser.objects.all()])
    if positive_tags:
      # first get all positive ones, intersect them
      for tag in positive_tags:
        user_tags = UserTag.objects.filter(tag__name=tag)
        people = set([user_tag.user.name for user_tag in user_tags])
        set_of_users = set_of_users.intersection(people)
    if negative_tags:
      # get all the negative tags, do set difference
      for tag in negative_tags:
        user_tags = UserTag.objects.filter(tag__name=tag)
        people = set([user_tag.user.name for user_tag in user_tags])
        set_of_users = set_of_users - people
    results = []
    user_tags_set = set()
    user_tags = UserTag.objects.filter(user__name=name)
    for user_tag in user_tags:
      user_tags_set.add(user_tag.tag.name)
    # tags for which the system will fetch top common words between queried user and each returned result (ex: top
    # music_lover words in common); only fetch for tags that the queried user has been classifed as
    top_common_words_tags = []
    for tag in positive_tags:
      if tag in user_tags_set:
        top_common_words_tags.append(tag)
    cossim = setup_and_run(name, top_common_words_tags)
    for user_obj in cossim:
      if user_obj["name"] in set_of_users:
        try:
          twitter_user = TwitterUser.objects.get(name=user_obj["name"])
          if len(allowed_users) > 0 and twitter_user in allowed_users:
            user_entry = {
              "twitter_handle": twitter_user.twitter_handle,
              "profile_picture": twitter_user.profile_image,
              "cosine_similarity": user_obj["cosine_similarity"],
              "name": user_obj["name"],
              "top_words_in_common": user_obj["top_words_in_common"],
              "top_tag_words_in_common": {}
            }
            for tag in top_common_words_tags:
              user_entry["top_tag_words_in_common"][tag] = user_obj[tag + "_top_words_in_common"]
            results.append(user_entry)
            if len(results) >= 10:
              break
        except TwitterUser.DoesNotExist:
          continue
        except Exception as e:
          continue
    results = results[:10]
  else:
    results = []
    cossim = setup_and_run(name)
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
