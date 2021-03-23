#################
# author: maups #
#################
import requests
import hashlib
import shutil
import gzip
import json
import sys
import os

####################
# helper functions #
####################

# download file from 'url', save it with 'filename'
def download_file(url, filename):
	with requests.get(url, stream=True) as r:
		r.raise_for_status()
		with open(filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192): 
				f.write(chunk)

# compute SHA256 hash string for a file
def compute_sha256(filename):
	sha256 = hashlib.sha256()
	with open(filename, 'rb') as f:
		for chunk in iter(lambda: f.read(8192),b""):
			sha256.update(chunk)
	return sha256.hexdigest()

# unzip file
def unzip_file(file_zipped, file_unzipped):
	with gzip.open(file_zipped, 'rb') as f_in:
		with open(file_unzipped, 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)

#####################################
# get ConceptNet English assertions #
#####################################

def get_conceptnet():

	def filter_conceptnet(file_all, file_filtered):
		with open(file_all, 'r') as f_in:
			with open(file_filtered, 'w') as f_out:
				line = f_in.readline()
				while line:
					v = line.split('\t')
					if v[2].startswith('/c/en/') and v[3].startswith('/c/en/'):
						meta = json.loads(v[4])
						f_out.write(v[1].split('/')[2] + '\t' + v[2].split('/')[3] + '\t' + v[3].split('/')[3] + '\t' + str(meta['weight']) + '\n')
					line = f_in.readline()

	conceptnet_url = 'https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz'

	conceptnet_filename_zipped = conceptnet_url.split('/')[-1]
	conceptnet_filename_zipped_hash = 'accd65fe94038584295574ddc26e1500c1919c8c4532bf771811cafd0948af7e'

	conceptnet_filename = conceptnet_filename_zipped[:-3]
	conceptnet_filename_hash = '40ad6e34b1bf86b013e46645fcb20e9b9c74091614c8b914c3c42f55c117afd2'

	conceptnet_filename_filtered = 'conceptnet-en-5.7.0.txt'
	conceptnet_filename_filtered_hash = 'e554b78c27825be13a7d6b8799c79c099ce8d425b2c6b24c80ef7652704ba482'

	print('Retrieving ConceptNet...')

	# check if one or more steps were completed
	flag_filter = True
	if os.path.isfile(conceptnet_filename_filtered):
		sha256 = compute_sha256(conceptnet_filename_filtered)
		if conceptnet_filename_filtered_hash == sha256:
			flag_filter = False

	flag_unzip = True
	if os.path.isfile(conceptnet_filename) and flag_filter:
		sha256 = compute_sha256(conceptnet_filename)
		if conceptnet_filename_hash == sha256:
			flag_unzip = False

	flag_download = True
	if os.path.isfile(conceptnet_filename_zipped) and flag_filter and flag_unzip:
		sha256 = compute_sha256(conceptnet_filename_zipped)
		if conceptnet_filename_zipped_hash == sha256:
			flag_download = False

	# download ConceptNet
	if flag_download and flag_unzip and flag_filter:
		download_file(conceptnet_url, conceptnet_filename_zipped)
		sha256 = compute_sha256(conceptnet_filename_zipped)
		if conceptnet_filename_zipped_hash != sha256:
			sys.exit('ConceptNet download failed!')
		print('Download OK!')
	else:
		print('Skipping download!')

	# unzip ConceptNet
	if flag_unzip and flag_filter:
		unzip_file(conceptnet_filename_zipped, conceptnet_filename)
		sha256 = compute_sha256(conceptnet_filename)
		if conceptnet_filename_hash != sha256:
			sys.exit('ConceptNet extraction failed!')
		os.remove(conceptnet_filename_zipped)
		print('Extraction OK!')
	else:
		print('Skipping extraction!')

	# filter English assertions from ConceptNet
	if flag_filter:
		filter_conceptnet(conceptnet_filename, conceptnet_filename_filtered)
		sha256 = compute_sha256(conceptnet_filename_filtered)
		if conceptnet_filename_filtered_hash != sha256:
			sys.exit('ConceptNet filtering failed!')
		os.remove(conceptnet_filename)
		print('Filtering OK!')
	else:
		print('Skipping filtering!')

	print('Done!\n')

##############################
# get NumberBatch embeddings #
##############################

def get_numberbatch():

	numberbatch_url = 'https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-en-19.08.txt.gz'

	numberbatch_filename_zipped = numberbatch_url.split('/')[-1]
	numberbatch_filename_zipped_hash = '90e57611eb71077ada9fd0b011fd0206de8ec13d035aced40b81b1a4d549c6a2'

	numberbatch_filename = numberbatch_filename_zipped[:-3]
	numberbatch_filename_hash = '42f92fcd49a63baf4d643bde39c996079432b383077afddebac20c2844c9a6f7'

	print('Retrieving NumberBatch...')

	# check if one or more steps were completed
	flag_unzip = True
	if os.path.isfile(numberbatch_filename):
		sha256 = compute_sha256(numberbatch_filename)
		if numberbatch_filename_hash == sha256:
			flag_unzip = False

	flag_download = True
	if os.path.isfile(numberbatch_filename_zipped) and flag_unzip:
		sha256 = compute_sha256(numberbatch_filename_zipped)
		if numberbatch_filename_zipped_hash == sha256:
			flag_download = False

	# download NumberBatch
	if flag_download and flag_unzip:
		download_file(numberbatch_url, numberbatch_filename_zipped)
		sha256 = compute_sha256(numberbatch_filename_zipped)
		if numberbatch_filename_zipped_hash != sha256:
			sys.exit('NumberBatch download failed!')
		print('Download OK!')
	else:
		print('Skipping download!')

	# unzip NumberBatch
	if flag_unzip:
		unzip_file(numberbatch_filename_zipped, numberbatch_filename)
		sha256 = compute_sha256(numberbatch_filename)
		if numberbatch_filename_hash != sha256:
			sys.exit('NumberBatch extraction failed!')
		os.remove(numberbatch_filename_zipped)
		print('Extraction OK!')
	else:
		print('Skipping extraction!')

	print('Done!\n')

########
# MAIN #
########

get_conceptnet()

get_numberbatch()

