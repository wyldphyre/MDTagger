#!/usr/bin/env python

# Permission denied when running the script in the shell? chmod 755 the script .py file

import sys
import os
import re
import subprocess
import titlecase


# COMIC_TAGGER_PATH = 'COMIC_TAGGER_PATH/Applications/ComicTagger.app/Contents/MacOS/ComicTagger'
COMIC_TAGGER_PATH = 'ComicTagger'  # and alias that points to the full path above
HANDLED_EXTENSIONS = ['.cbr', '.cbz']


def cleanFilenameIssue(source):
    assert isinstance(source, str)
    return source.lstrip('0')


def cleanFilenameTitle(source):
    assert isinstance(source, str)
    return titlecase.titlecase(source.replace('.', ' ').lstrip().rstrip())


def escapeForShell(source):
    assert isinstance(source, str)
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')


def escapeForComicTagger(source):
    assert isinstance(source, str)
    return source.replace(',', '^,').replace('=', '^=')


def outputHelp():
    # print 'Usage: ComicTagger [OPTION]... [FOLDER]'
    print ''
    print 'Usage: ComicTagger [OPTIONS] [FILE|FOLDER]'
    print ''
    print 'A utility for detecting Issue and Titles from comic archives downloaded with manga_downloader (https://github.com/jiaweihli/manga_downloader), then inserting that information into the archive using ComicTagger'
    print ''
    print 'The name of all files in the specified folder, or the specified file, will be examined for issue number and title and then the user is asked if the data should be inserted'
    print ''
    print 'Options:'
    print '-a  :  automatically updates comic archives without asking user for comfirmation'
    print ''


def parseExistingTags(data):
    assert isinstance(data, str)

    # validate
    start_index = data.find('------ComicRack tags--------')
    if start_index == -1:
        return []

    data = data[data.find('\n', start_index) + 1:]

    lines = data.splitlines()
    tags = {}

    for line in lines:
        if line == '':
            continue

        pieces = line.split(':', 1)

        if len(pieces) > 0 and pieces[1] != '':
            tags[pieces[0]] = pieces[1].strip(' ')

    return tags


def processFile(file_path, auto_update):
    assert isinstance(file_path, str)
    assert isinstance(auto_update, bool)

    # check that file is a comic archive
    filename = os.path.split(file_path)[1]
    extension = os.path.splitext(file_path)[1]

    if not extension in HANDLED_EXTENSIONS:
        print "Skipping %s. Not a comic archive" % filename
        return

    print "Processing: %s" % filename

    # look for the issue number and title
    filename_volume = ""
    filename_issue = ""
    filename_title = ""

    # look for volume and chapter match i.e. chiis.sweet.home.MangaHere.v005.c017.cbz
    match = re.search('\.v(\d*)\.c(.*)\.cbz|cbr', filename)
    if match:
        filename_volume = match.group(1)
        filename_issue = match.group(2)
    else:
        match = re.search('\.(\d*)\.\.(.*)\.cbz|cbr', filename)
        if match:
            filename_issue = match.group(1)
            filename_title = match.group(2)
        else:
            match = re.search('\.c?(\d*)\.cbz|cbr', filename)
            if match:
                filename_issue = match.group(1)

    if not match:
        print "Could not locate a title or issue number in: %s" % filename
    else:
        if filename_volume != "":
            filename_volume = cleanFilenameIssue(filename_volume)
            print "Found Volume: %s" % filename_volume

        if filename_issue != "":
            filename_issue = cleanFilenameIssue(filename_issue)
            print "Found Issue: %s" % filename_issue

        if filename_title != "":
            filename_title = cleanFilenameTitle(filename_title)
            print "Found Title: %s" % filename_title

        process = subprocess.Popen('%s -p %s' % (COMIC_TAGGER_PATH, escapeForShell(file_path)), stdout=subprocess.PIPE, shell=True)
        existing_tags = parseExistingTags(process.stdout.read())

        needs_update = \
            (filename_issue != '' and (not 'issue' in existing_tags or (filename_issue != existing_tags['issue']))) or \
            (filename_title != '' and (not 'title' in existing_tags or (filename_title != existing_tags['title']))) or \
            (filename_volume != '' and (not 'volume' in existing_tags or (filename_volume != existing_tags['volume'])))

        if needs_update:
            do_update = auto_update or raw_input("Update tags for this file? (y/n): ") == "y"

            if do_update:
                metadata_statement = produceComicTaggerMetaDataStatement(filename_volume, filename_issue, filename_title)
                command = '%s -s -m "%s" -t cr %s' % (COMIC_TAGGER_PATH, metadata_statement, escapeForShell(file_path))

                return_code = subprocess.call(command, shell=True)
                if return_code != 0:
                    print "Return code: %s" % return_code
        else:
            print 'Tags already match found data. Skipping archive.'
    print ""


def produceComicTaggerMetaDataStatement(volume, issue, title):
    assert isinstance(issue, str)
    assert isinstance(title, str)

    tags = []

    if volume != "":
        tags.append("volume=%s" % volume)

    if issue != "":
        tags.append("issue=%s" % issue)

    if title != "":
        tags.append("title=%s" % escapeForComicTagger(title))

    return ','.join(tags)


# Main program method
def MDTagger():
    arguments = sys.argv

    if len(arguments) < 2:  # the sys.argv[0] contains the script name, so there is always at least one argument
        outputHelp()
        quit()

    path = ""
    auto_update = False

    for param in arguments[1:]:
        if param.startswith('-'):
            if param == '-a':
                auto_update = True
            else:
                print "Unknown options %s" % param
                quit()
        else:
            if path != "":
                print "Only one file or folder path can be specified"
                quit()
            else:
                path = param

    if path == "":
        print "You must specify a file or folder to operate on"
        quit()

    if os.path.isdir(path):
        directory_list = os.listdir(path)

        for filename in directory_list:
            file_path = os.path.join(path, filename)

            if os.path.isfile(file_path):
                processFile(file_path, auto_update)

    elif os.path.isfile(path):
        processFile(path, auto_update)


# Start of execution
MDTagger()
