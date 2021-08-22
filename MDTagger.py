#!/usr/bin/env python

# Permission denied when running the script in the shell? chmod 755 the script .py file

import sys
import os
import re
import subprocess
import titlecase


# COMIC_TAGGER_PATH = 'COMIC_TAGGER_PATH/Applications/ComicTagger.app/Contents/MacOS/ComicTagger'
COMIC_TAGGER_PATH = 'ComicTagger'  # and alias that points to the full path above
HANDLED_EXTENSIONS = ['.cbr', '.cbz', '.zip']


def cleanFilenameIssue(source):
    assert isinstance(source, str)
    return source.lstrip('ch').lstrip('0')

def cleanFilenameVolume(source):
    assert isinstance(source, str)
    return source.lstrip('v').lstrip('0')

def cleanFilenameArtist(source):
    assert isinstance(source, str)
    return source.lstrip('(').rstrip(')')

def cleanFilenameSeries(source):
    assert isinstance(source, str)
    # return titlecase.titlecase(source.replace('.', ' ').lstrip().rstrip())
    return source.replace('.', ' ').lstrip().rstrip()
    

def escapeForShell(source):
    assert isinstance(source, str)
    return source.replace(' ', '\ ').replace('(', '\(').replace(')', '\)').replace('[', '\[').replace(']', '\]')
    # should perhaps be using 'r' to make raw strings in order to avoid the pylint comments on the above (and elsewhere)


def escapeForComicTagger(source):
    assert isinstance(source, str)
    return source.replace(',', '^,').replace('=', '^=')


def outputHelp():
    # print 'Usage: ComicTagger [OPTION]... [FOLDER]'
    print ''
    print 'Usage: ComicTagger [OPTIONS] [FILE|FOLDER]'
    print ''
    print 'A utility for detecting Issue and Series from comic archives filenames, then inserting that information into the archive using ComicTagger'
    print ''
    print 'The name of the specified file (or each file in a specified folder), will be examined for issue number and title and then the user is asked if the data should be inserted into the archive'
    print ''
    print 'Options:'
    print '-a  :  automatically updates comic archives without asking user for confirmation'
    print ''


def parseExistingTags(data):
    assert isinstance(data, str)

    # validate
    start_index = data.find('------ ComicRack tags --------')
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

    # look for the issue number and series
    filename_volume = ""
    filename_issue = ""
    filename_series = ""
    filename_artist = ""

    # look for volume and chapter match i.e. chiis.sweet.home.MangaHere.v005.c017.cbz
    # match = re.search('\.(\d*)\.\.(.*)\.cbz|cbr', filename)
    # try to match with an artist name first
    match = re.search('^(\(.*\))\s(.*)\s((?:ch\s*)?\d*)\s', filename)
    if match:
        filename_artist = match.group(1)
        filename_series = match.group(2)
        filename_issue = match.group(3)
    else:
        # try to match just a series and issue number with 'ch' prefix
        match = re.search('^(.*)\s((?:ch\s*)?\d*)\s', filename)
        if match:
            filename_series = match.group(1)
            filename_issue = match.group(2)
        else:
            # try to match just a series and issue number without 'ch' prefix
            match = re.search('^(.*)\s(\d*)\s', filename)
            if match:
                filename_series = match.group(1)
                filename_issue = match.group(2)
            else:
                match = re.search('\s?v(\d*)\s?', filename)
                if match:
                    filename_volume = match.group(1)

    if not match:
        print "Could not locate a series or issue number in: %s" % filename
    else:
        if filename_volume != "":
            filename_volume = cleanFilenameVolume(filename_volume)
            print "Found Volume: %s" % filename_volume

        if filename_issue != "":
            filename_issue = cleanFilenameIssue(filename_issue)
            print "Found Issue: %s" % filename_issue

        if filename_series != "":
            filename_series = cleanFilenameSeries(filename_series)
            print "Found Title: %s" % filename_series

        if filename_artist != "":
            filename_artist = cleanFilenameArtist(filename_artist)
            print "Found Artist: %s" % filename_artist

        process = subprocess.Popen('%s -p %s' % (COMIC_TAGGER_PATH, escapeForShell(file_path)), stdout=subprocess.PIPE, shell=True)
        existing_tags = parseExistingTags(process.stdout.read())

        needs_update = \
            (filename_issue != '' and (not 'issue' in existing_tags or (filename_issue != existing_tags['issue']))) or \
            (filename_series != '' and (not 'series' in existing_tags or (filename_series.lower() != existing_tags['series'].lower()))) or \
            (filename_volume != '' and (not 'volume' in existing_tags or (filename_volume != existing_tags['volume']))) or \
            (filename_artist != '' and (not 'credit' in existing_tags or not filename_artist in existing_tags['credit']))

        if needs_update:
            do_update = auto_update or raw_input("Update tags for this file? (y/n): ") == "y"

            if do_update:
                metadata_statement = produceComicTaggerMetaDataStatement(filename_volume, filename_issue, filename_series, filename_artist)
                command = '%s -s -m "%s" -t cr %s' % (COMIC_TAGGER_PATH, metadata_statement, escapeForShell(file_path))

                return_code = subprocess.call(command, shell=True)
                if return_code != 0:
                    print "Return code: %s" % return_code
        else:
            print 'Tags already match found data. Skipping archive.'
    print ""


def produceComicTaggerMetaDataStatement(volume, issue, series, artist):
    assert isinstance(issue, str)
    assert isinstance(series, str)

    tags = []

    if volume != "":
        tags.append("volume=%s" % volume)

    if issue != "":
        tags.append("issue=%s" % issue)

    if series != "":
        tags.append("series=%s" % escapeForComicTagger(series))

    if artist != "":
        tags.append("credit=Artist:%s" % artist)

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
