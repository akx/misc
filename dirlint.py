import argparse
import os
import shutil


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('root')
	ap.add_argument('--unnest', action='store_true', default=False)
	ap.add_argument('--remove-empty', action='store_true', default=False)
	args = ap.parse_args()


	for dirname, dirnames, filenames in os.walk(args.root):
		dirpath = os.path.join(args.root, dirname)
		kind = None
		if not filenames and dirnames == [os.path.basename(dirname)]:
			kind = 'Nested'
		elif not (dirnames or filenames):
			kind = 'Empty'
		elif dirnames and not filenames:
			kind = 'Only subdirectories'

		if kind:
			print(kind, ':', dirpath)

		if kind == 'Empty' and args.remove_empty:
			os.rmdir(dirpath)
			continue

		if kind == 'Nested' and args.unnest:
			assert len(dirnames) == 1
			src_dir = os.path.join(args.root, dirname, dirnames[0])
			dest_dir = dirpath
			for file in os.listdir(src_dir):
				src_file = os.path.join(src_dir, file)
				dest_file = os.path.join(dest_dir, file)
				shutil.move(src_file, dest_file)
			os.rmdir(src_dir)
				


if __name__ == '__main__':
	main()