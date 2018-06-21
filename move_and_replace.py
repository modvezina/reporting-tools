import careful_replacer as replace
import os
import shutil

source_path = "//path/"
target_path = '//path/'


for file in os.listdir(source_path):
	file_path = source_path+ file
	isfile = os.path.isfile(file_path)
	isPDF = file[-4:] == ".pdf"
	if isfile and isPDF:
		shutil.copy2(file_path,target_path)
		print('Done! '+ file)