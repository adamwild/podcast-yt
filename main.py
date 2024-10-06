if __name__ == '__main__':
	import sys
	import argparse
 
	import os
	folder_main = os.path.dirname(os.path.realpath(__file__))
	sys.path.append(folder_main)
	sys.stdout.reconfigure(encoding='utf-8')

	parser = argparse.ArgumentParser()

	parser.add_argument('link', help='The link to the video')
	parser.add_argument("-sub", "--subtitles", help="downloads subtitles", action="store_true")

	args = parser.parse_args()

	from src.basic import Basic
 
	if args.subtitles:
		subs = True
	else:
		subs = False
  
	bsc = Basic()
	bsc.download(args.link, subs)

