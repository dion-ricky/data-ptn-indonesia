#!/usr/bin/python3
import re
import json
import requests
from bs4 import BeautifulSoup

def fetch(url):
	r = requests.get(url)
	if is_good_response(r):
		return r

	log_error("url fetch. Invalid response!")
	return None

def is_good_response(r):
	content_type = r.headers['Content-Type'].lower()
	return (r.status_code == 200
			and content_type is not None
			and content_type.find('html') > -1
			)

def souper(r):
	if type(r) == requests.models.Response:
		return BeautifulSoup(r.text, 'html.parser')

	log_error("response souper. Parameter is not a valid response!")
	return None

def data_getter(s, t, c=None):
	if c is not None:
		data = s.find(t, class_=c)
	else:
		data = s.find(t)
	return data

def log_error(e):
	print("Error: {}".format(e))

def file_writer(fname, c):
	if type(c) == str:
		with open(fname, "w") as _file:
			_file.write(c)
		return

	log_error("write file. Content parameter is not string")

def regex_parser(p, s):
	regex = re.compile(p)
	matches = regex.finditer(s)
	if matches is not None:
		return matches

	log_error("regex parsing. Regex did not match with the string")
	return None

def get_prodi_data(id_ptn):
	print("Fetching raw data...")
	raw = souper(fetch("http://sbmptn.ltmpt.ac.id/?mid=14&ptn={}".format(id_ptn)))
	univ_name = data_getter(raw, "a", "panel-title").text

	saintek = raw.find(id="jenis1")
	soshum = raw.find(id="jenis2")

	if saintek is not None:
		saintek = saintek.tbody

	if soshum is not None:
		soshum = soshum.tbody

	pattern = r"(\d+)\s+([a-zA-Z\(\)\.\ ]+)\s+([\d\.]*)\s+([\d\.]*)\s+([\d]*)"

	saintek_arr = []
	soshum_arr = []

	print("Parsing data...")
	if saintek is not None:
		for match in regex_parser(pattern, saintek.text):
			print("ID Prodi: {}".format(match.group(1)))
			print("Nama: {}".format(match.group(2)))
			saintek_arr.append([match.group(1), match.group(2), match.group(3), match.group(4)])

	if soshum is not None:
		for match in regex_parser(pattern, soshum.text):
			print("ID Prodi: {}".format(match.group(1)))
			print("Nama: {}".format(match.group(2)))
			soshum_arr.append([match.group(1), match.group(2), match.group(3), match.group(4)])

	print("Preparing for saving data in json...")
	data = {
		"ID": id_ptn,
		"Nama Universitas" : univ_name,
		"Program Studi" : {
			"SAINTEK" : saintek_arr,
			"SOSHUM" : soshum_arr
		}
	}

	print("Saving data...")
	file_writer("./data_prodi/{}.json".format(univ_name), json.dumps(data))

def main():
	print("Fetching raw data...")
	url = "http://sbmptn.ltmpt.ac.id/?mid=14"
	raw = souper(fetch(url))
	table = data_getter(raw, "table", "table table-striped")
	pattern = r'\s*(\d{3})\s*([\w\ \"]+)'
	data = []
	print("Parsing data...")
	for match in regex_parser(pattern, table.text):
		data.append([match.group(1), match.group(2)])

	print("Saving data...")
	file_writer("data_prodi.json", json.dumps(data))

	for d in data:
		print("Fetching data from University ID: {}".format(d[0]))
		get_prodi_data(d[0])

if __name__ == '__main__':
	main()
