import os
import django
from project_template.models import Docs

def docs_init():
	root_path = "../docs"
	for root, dirs, files in os.walk(root_path):
		for f in files:
			d = Docs(address = root+f)
			d.save()

docs_init()