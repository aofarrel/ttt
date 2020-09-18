import io
import os
import firecloud.api as fapi
import google.cloud.storage
import pandas as pd
import logging

def setGlobals(BILLING_PROJECT_ID, WORKSPACE, BUCKET, SUBDIRECTORY):
	# I don't care if it's cursed, I'm doing this.
	global BILLING_PROJECT_ID 
	BILLING_PROJECT_ID = BILLING_PROJECT_ID
	global WORKSPACE
	WORKSPACE = WORKSPACE
	global BUCKET
	BUCKET = BUCKET
	global SUBDIRECTORY
	SUBDIRECTORY = SUBDIRECTORY

def callFirecloud():
	try:
		response = fapi.list_entity_types(BILLING_PROJECT_ID, WORKSPACE)
		if response.status_code != 200:
			print("Error in Firecloud, check your billing project ID and the name of your workspace.")
			raise
		else:
			print("Firecloud has found your workspace!")
			directory = BUCKET + SUBDIRECTORY
			return directory
	except NameError:
		print("Caught a NameError exception. This may mean the kernal was restarted or you didn't run ",
			  "the cells above. Try running the cells above again.")
		raise

def _initLogger_():
	logger = logging.getLogger('')
	logger.setLevel(logging.INFO)
	return logger

def _clipGS_(string BUCKET):
	google_storage_prefix = 'gs://'
	if BUCKET.startswith(google_storage_prefix):
		clippedBucket = BUCKET[len(google_storage_prefix):]  # clip off "gs://" prefix
	else return BUCKET

def _initDataframe_():
	# Called by parseLs()
	df = pd.DataFrame()
	return df

def parseLs(string directory):
	df = initDataframe()
	logging.info("Querying your GCS bucket...")
	os.system(gsutil ls $directory > ls.txt)
	with open("ls.txt", "r") as this_file:
		df['location'] = this_file.read().splitlines()
		return df

def splitOnFileExt(df):
	''' Split on file extension and count how many child file extensions there are.
	Inputs:
		* df (type Pandas Dataframe)
	Outputs:
		* unique_children (type list) - list of how unique child file types.
			For example, if the only child type is crai, it's just ["crai"]. '''
	logger = _initLogger_()
	df['FileType'] = df.location.str.rsplit('.', 1).str[-1]
	unique_children = pd.unique(df[['FileType']].values.ravel("K"))
	logging.info("{0} unique file extensions (including parent) have been found.".format(len(unique_children)))
	unique_children = unique_children[unique_children!=PARENT_FILETYPE]
	logging.info("Child file types are: %s  If this looks wrong, check your GCS directory for missing or junk files." % unique_children)
	return unique_children

# Link parents and children; this part takes the longest
def linker(unique_children):
	# init
	logger = _initLogger_()
	storage_client = google.cloud.storage.Client()
	subdirectory_chopped = SUBDIRECTORY.strip("/")
	logging.info("Linking parents and children...")
	list_dfs = [] # List of dataframes, one df per child extension
	for child in unique_children:
	    list_of_list_child = []
	    progress(child, unique_children)    
		for blob in storage_client.list_blobs(clippedBucket, prefix=subdirectory_chopped):
			if blob.name.endswith(PARENT_FILETYPE):
				# remove PARENT_FILETYPE extension and search for basename
				basename = blob.name[:-len(f'.{PARENT_FILETYPE}')]
				for basename_blob in storage_client.list_blobs(clippedBucket, prefix=basename):
					if basename_blob.name.endswith(child):
						parent_filename = blob.name.split('/')[-1]
						child_filename = basename_blob.name.split('/')[-1]
						parent_location = f'{google_storage_prefix}{clippedBucket}/{blob.name}'
						child_location  = f'{google_storage_prefix}{clippedBucket}/{basename_blob.name}'
						list_child = ([parent_filename, parent_location, child_filename, child_location])
						list_of_list_child.append(list_child)
						# If no child is found, the parent will not be added to the df at all
		df_child = pd.DataFrame(list_of_list_child, columns=[
			'parentFile', 
			'parentLocation',child+'File', child+'Location'])
		list_dfs.append(df_child)
	return list_dfs

def mergeDfs(list_dfs):
	logger = _initLogger_()
	logging.info("Merging dataframes...")
	merged_df = pd.DataFrame()
	for df in list_dfs:
		try:
			merged_df = merged_df.merge(df, on=['parentFile', 'parentLocation'])
		except KeyError:
			# Should only happen first iteration
			merged_df = df
	logging.info("Finished!")


def _linkerProgress_(current_child, unique_children):
	# Keeps track of linker's progress
	if current_child not in unique_children:
		# Should never happen unless user edits code incorrectly
		logging.error("Invalid child extension")
		raise
	else:
		unique_children_list = unique_children.tolist()
		logging.info("\t\t Processing {0} files... ({1} out of {2})".format(current_child, 
			unique_children_list.index(current_child)+1, 
			len(unique_children_list)))


def __main__():
	# do stuff to get WORKSPACE and BILLING_PROJECT_ID
	setGlobals(BILLING_PROJECT_ID, WORKSPACE, BUCKET)
	directory = callFirecloud()
	linker(unique_children)
	mergeDfs()