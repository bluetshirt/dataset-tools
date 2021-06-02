#dupe eliminator
#adapted from dschultz's dataset-tools
#now it doesn't really fit anymore
#to install dependencies run this command:
#pip install dhash pybktree Pillow

import argparse
import dhash
import pybktree
import collections
import os
import PIL
import shutil

DUPES_FOLDER = "dupes/"
UNIQUE_FOLDER = "unique/"

def parse_args():
	desc = "Eliminate duplicates from a directory of images" 
	parser = argparse.ArgumentParser(description=desc)

	parser.add_argument('-v', '--verbose', action='store_true',
		help='Print progress to console.')

	parser.add_argument('-i', '--input_folder', type=str,
		default='./input/',
		help='Directory path to the inputs folder. (default: %(default)s)')

	parser.add_argument('-o', '--output_folder', type=str,
		default='./output/',
		help='Directory path to the outputs folder. (default: %(default)s)')

	parser.add_argument('-t', '--threshold', type=float,
		default=2,
		help='Increase to raise sensitivity. Decrease to reduce false dupe matches (default: %(default)s)')

	parser.add_argument('-n', '--list-only', action='store_true',
		help='Do not copy any files to output directory. Duplicates will be identified and listed.')
	
	args = parser.parse_args()
	return args

#returns the number of bits different between the two hash codes
def perceptual_distance(x, y):
	return pybktree.hamming_distance(x.hash, y.hash)

def copy_img(img_name, dest_folder):

	abs_output_folder = os.path.abspath(os.path.join(args.output_folder, dest_folder))
	dest_img_name = img_name.replace(abs_input_folder, abs_output_folder, 1)	
	dest_img_dir = os.path.dirname(dest_img_name)
	
	os.makedirs(dest_img_dir, exist_ok=True)
	shutil.copy(img_name, dest_img_dir)
	
def copy_dupe(img_name):
	copy_img(img_name, DUPES_FOLDER)
	
def copy_unique(img_name):
	copy_img(img_name, UNIQUE_FOLDER)

#define a named tuple with two fields: filename and hash
HashEntry = collections.namedtuple('HashEntry', 'filename hash')
		
#main line starts here

args = parse_args()

abs_input_folder = os.path.abspath(args.input_folder)

#this is a special data structure that lets us find other objects with a similar hash
tree = pybktree.BKTree(perceptual_distance, [])

image_names = []
dupe_count = 0

for dirpath, dnames, fnames in os.walk(args.input_folder):
    for f in fnames:
        if f.lower().endswith(".jpg") or f.lower().endswith(".png"):
            image_names.append(os.path.abspath(os.path.join(dirpath, f)))

for image_name in image_names:
	img = PIL.Image.open(image_name)
	entry = HashEntry(image_name, dhash.dhash_int(img))

	found = tree.find(entry, args.threshold)
	if found:
		dupe_count += 1
		if args.verbose or args.list_only:
			print (f"{image_name} ~{found[0][0]}~ {found[0][1].filename}")
		if not args.list_only:
			copy_dupe(image_name)
	else:
		tree.add(entry)
		if not args.list_only:
			copy_unique(image_name)
			
print()
print(f"{len(image_names)} image(s) checked.") 
print(f"{dupe_count} duplicate(s) found.")
if args.list_only:
	print("(no images were copied)")
	