#!/usr/bin/env python

# Permission denied when running the script in the shell? chmod 755 the script .py file

import sys
import os
import re
import subprocess
import titlecase


# COMIC_TAGGER_PATH = 'COMIC_TAGGER_PATH/Applications/ComicTagger.app/Contents/MacOS/ComicTagger'
COMIC_TAGGER_PATH = 'ComicTagger'


def clean_filename_issue(source):
    assert isinstance(source, str)
    return source.lstrip('0')


def escape_for_shell(source):
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


def escape_for_comictagger(source):
    return source.replace(',', '^,').replace('=', '^=')


def clean_filename_title(source):
    return titlecase.titlecase(source.replace('.', ' ').lstrip().rstrip())


def show_help():
    # print 'Usage: ComicTagger [OPTION]... [FOLDER]'
    print ''
    print 'Usage: ComicTagger [FOLDER]'
    print ''
    print 'A utility for detecting Issue and Titles from comic archives downloaded with manga_downloader (https://github.com/jiaweihli/manga_downloader), then inserting that information into the archive using ComicTagger'
    print ''
    print 'The name of all files in the specified folder will be examined for issue number and title and then the user is asked if the data should be inserted'
    print ''


#def issue_is_valid(issue):
#    return str.isdigit(issue)


arguments = sys.argv

if len(arguments) < 2:  # the sys.argv[0] contains the script name, so there is always at least one argument
    show_help()
    quit()

folder_name = arguments[1]

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
            filename_issue = match.group(1)
            filename_title = match.group(2)

            filename_issue = clean_filename_issue(filename_issue)
            filename_title = clean_filename_title(filename_title)

            print "Found Issue: %s" % filename_issue
            print "Found Title: %s" % filename_title

            # todo: check existing tags and report/skip if there is no work to do
            # command = '%s -p %s' % (COMIC_TAGGER_PATH, escape_spaces(full_file_path))

            # Ask user for permission to modify
            answer = raw_input("Update tags for this file? (y/n): ")

            if answer == "y":
                command = '%s -s -m "title=%s,issue=%s" -t cr %s' % (COMIC_TAGGER_PATH, escape_for_comictagger(filename_title), filename_issue, escape_for_shell(full_file_path))
                return_code = subprocess.call(command, shell=True)
                # if return_code != 0:
                #     print "Return code: %s" % return_code
        else:
            print "Could not locate a title and issue number in: %s" % filename

        print ""