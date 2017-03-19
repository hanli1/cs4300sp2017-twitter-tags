from .models import Docs
import os
import Levenshtein
import json


def read_file(n):
	path = Docs.objects.get(id = n).address;
	file = open(path)
	transcripts = json.load(file)
	return transcripts

def _edit(query, msg):
    return Levenshtein.distance(query.lower(), msg.lower())

def find_similar(q):
	transcripts = read_file(1)
	result = []
	for transcript in transcripts:
		for item in transcript:
			m = item['text']
			result.append(((_edit(q, m)), m))

	return sorted(result, key=lambda tup: tup[0])