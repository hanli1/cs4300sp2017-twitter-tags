from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import simplejson as json
from django.http import JsonResponse
import os
import numpy as np
from .models import UserTag

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
    output_list = find_similar(search)
    paginator = Paginator(output_list, 10)
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
  print search
  print tags

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
  print results
  data["results"] = results
  return JsonResponse(data)

users = []
def get_users_handles(request):
  global users

  if len(users) == 0:
    # first time, load from disk
    with open(os.path.dirname(__file__) + "/../scripts/data_retrieval/top_users_handle.txt", "r+") as f1:
      all_handles = f1.readlines()
      with open(os.path.dirname(__file__ ) + "/../scripts/data_retrieval/top_users_name.txt", "r+") as f2:
        all_names = f2.readlines()
        users = [{"value": i + " " + j} for i, j in zip(all_handles, all_names)]

  data = {}
  data["suggestions"] = users
  # data["suggestions"] = [{"value":"hello"}]
  return JsonResponse(data)

tags = []
def get_tag_labels(request):
  global tags

  if len(tags) == 0:
    # first time, load from disk
    # with open(os.path.dirname(__file__) + "/../scripts/data_retrieval/top_users_handle.txt", "r+") as f1:
    #   all_handles = f1.readlines()
    #   with open(os.path.dirname(__file__) + "/../scripts/data_retrieval/top_users_name.txt", "r+") as f2:
    #     all_names = f2.readlines()
    #     users = [{"value": i + " " + j} for i, j in zip(all_handles, all_names)]
    og_tags = [u'liberal', u'food_lover', u'music_lover', u'art_lover', u'science_lover', u'gamer', u'sports_fan', u'fashion_lover', u'conservative', u'religious']
    tags = [{"value": i} for i in og_tags]

  data = {}
  data["suggestions"] = tags
  return JsonResponse(data)
