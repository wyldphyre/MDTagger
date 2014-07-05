import sys
import os
import re
import subprocess
import titlecase


# COMIC_TAGGER_PATH = 'COMIC_TAGGER_PATH/Applications/ComicTagger.app/Contents/MacOS/ComicTagger'
COMIC_TAGGER_PATH = 'ComicTagger'


def clean_issue(source):
    assert isinstance(source, str)
    return source.lstrip('0')


def escape_for_shell(source):
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


def escape_for_comictagger(source):
    return source.replace(',', '^,').replace('=', '^=')


def clean_title(source):
    return titlecase.titlecase(source.replace('.', ' ').lstrip().rstrip())


#def issue_is_valid(issue):
#    return str.isdigit(issue)


# todo: allow script to run in interactive mode
# Interactive mode would let the user provide a simple y/n answer
# as to whether each files extracted info should be saved to file

folder_name = sys.argv[1]
print folder_name

if not os.path.isdir(folder_name):
    print "Parameter must be a folder"
    quit()

directory_list = os.listdir(folder_name)

for filename in directory_list:
    full_file_path = os.path.join(folder_name, filename)

    if os.path.isfile(full_file_path):
        print "Processing: %s" % filename
        # look for the issue number and title
        match = re.search('\.(\d*)\.\.(.*)\.cbz|cbr', filename)
        if match:
            issue = match.group(1)
            title = match.group(2)

            issue = clean_issue(issue)
            title = clean_title(title)

            # todo: validate issue is a clean usable number

            print "Found Issue: %s" % issue
            print "Found Title: %s" % title

            # todo: check existing tags and report/skip if there is no work to do
            # command = '%s -p %s' % (COMIC_TAGGER_PATH, escape_spaces(full_file_path))

            # Ask user for permission to modify
            answer = raw_input("Update tags for this file? (y/n): ")

            if answer == "y":
                command = '%s -s -m "title=%s,issue=%s" -t cr %s' % (COMIC_TAGGER_PATH, escape_for_comictagger(title), issue, escape_for_shell(full_file_path))
                return_code = subprocess.call(command, shell=True)
                # if return_code != 0:
                #     print "Return code: %s" % return_code

        print ""