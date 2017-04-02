from __future__ import unicode_literals

import os
import sys
import logging
import json
import re
import itertools
import time

from flask import Flask, Response
from flask import request, abort
from flask_cors import CORS, cross_origin

import query_builder

application = Flask(__name__)
CORS(application)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

@application.route("/")
def index():
	return "Hoax Analyzer - Query Extractor API"

@application.route("/extract/text", methods=['POST'])
def extract_text():
	try:
		text = request.json['text']
		query = query_builder.build_query_from_text(text)
		result = json.dumps(query)
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/extract/image", methods=['POST'])
def extract_image():
	try:
		image = request.json['image']
		f = image ## TO-DO: kirim image melalui HTTP
		b = bytearray(f)
		result1 = query_builder.image_to_text(b)
		text = json.loads(result1)["text"]
		result = query_builder.build_query_from_image(text)
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response

if __name__ == "__main__":
	application.run(host="0.0.0.0", port=8080)