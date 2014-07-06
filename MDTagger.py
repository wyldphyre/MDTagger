#!/usr/bin/env python

# Permission denied when running the script in the shell? chmod 755 the script .py file

import sys
import os
import re
import subprocess
import titlecase


# COMIC_TAGGER_PATH = 'COMIC_TAGGER_PATH/Applications/ComicTagger.app/Contents/MacOS/ComicTagger'
COMIC_TAGGER_PATH = 'ComicTagger'  # and alias that points to the full path above


def cleanFilenameIssue(source):
    assert isinstance(source, str)
    return source.lstrip('0')


def cleanFilenameTitle(source):
    return titlecase.titlecase(source.replace('.', ' ').lstrip().rstrip())


def escapeForShell(source):
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


def escapeForComicTagger(source):
    return source.replace(',', '^,').replace('=', '^=')


def outputHelp():
    # print 'Usage: ComicTagger [OPTION]... [FOLDER]'
    print ''
    print 'Usage: ComicTagger [FOLDER]'
    print ''
    print 'A utility for detecting Issue and Titles from comic archives downloaded with manga_downloader (https://github.com/jiaweihli/manga_downloader), then inserting that information into the archive using ComicTagger'
    print ''
    print 'The name of all files in the specified folder will be examined for issue number and title and then the user is asked if the data should be inserted'
    print ''


def processFile(target_filename):
    print "Processing: %s" % target_filename

    # look for the issue number and title
    filename_issue = ""
    filename_title = ""

    match = re.search('\.(\d*)\.\.(.*)\.cbz|cbr', target_filename)
    if match:
        filename_issue = match.group(1)
        filename_title = match.group(2)
    else:
        match = re.search('\.c?(\d*)\.cbz|cbr', target_filename)
        if match:
            filename_issue = match.group(1)

    if not match:
        print "Could not locate a title or issue number in: %s" % target_filename
    else:
        if filename_issue != "":
            filename_issue = cleanFilenameIssue(filename_issue)
            print "Found Issue: %s" % filename_issue

        if filename_title != "":
            filename_title = cleanFilenameTitle(filename_title)
            print "Found Title: %s" % filename_title

        # todo: check existing tags and report/skip if there is no work to do
        # command = '%s -p %s' % (COMIC_TAGGER_PATH, escape_spaces(full_file_path))

        # Ask user for permission to modify
        answer = raw_input("Update tags for this file? (y/n): ")

        if answer == "y":
            if filename_issue != "" and filename_title != "":
                command = '%s -s -m "title=%s,issue=%s" -t cr %s' % (COMIC_TAGGER_PATH, escapeForComicTagger(filename_title), filename_issue, escapeForShell(full_file_path))
            elif filename_issue != "":
                command = '%s -s -m "issue=%s" -t cr %s' % (COMIC_TAGGER_PATH, filename_issue, escapeForShell(full_file_path))

            return_code = subprocess.call(command, shell=True)
            if return_code != 0:
                print "Return code: %s" % return_code
    print ""


# Start of execution

arguments = sys.argv

if len(arguments) < 2:  # the sys.argv[0] contains the script name, so there is always at least one argument
    outputHelp()
    quit()

folder_name = arguments[1]

if not os.path.isdir(folder_name):
    print "Parameter must be a folder"
    quit()

directory_list = os.listdir(folder_name)

for filename in directory_list:
    full_file_path = os.path.join(folder_name, filename)

    if os.path.isfile(full_file_path):
        processFile(filename)