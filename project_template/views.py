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

def get_users_handles(request):
  user_handles = [{
        "value": "United Arab Emirates",
        "data": "AE"
    }, {
        "value": "United Kingdom",
        "data": "UK"
    }, {
        "value": "United States",
        "data": "US"
    }, {
        "value": "United Funes",
        "data": "DAN"
    }]
  data = {}
  data["suggestions"] = user_handles
  return JsonResponse(data)
