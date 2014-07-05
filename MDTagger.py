import sys, os, re
import titlecase


def clean_issue(source):
    return source.lstrip('0')


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
    print "Parameter must be a directory"
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

        print ""