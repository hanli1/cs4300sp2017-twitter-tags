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

# Create your views here.
def index(request):
  output_list = ''
  output=''
  if request.GET.get('search'):
    search = request.GET.get('search')
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

users = []
def get_users_handles(request):
  global users

  if len(users) == 0:
    # first time, load from disk
    with open(os.path.dirname(__file__) + "/../scripts/data_retrieval/top_users_handle.txt", "r+") as f1:
      all_handles = f1.readlines()
      with open(os.path.dirname(__file__) + "/../scripts/data_retrieval/top_users_name.txt", "r+") as f2:
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
    tags = [{"value": "food"}, {"value": "democrats"}]

  data = {}
  data["suggestions"] = tags
  return JsonResponse(data)
