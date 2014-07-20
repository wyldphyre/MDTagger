MDTagger
========

A simple script to parse comic issue numbers and titles out of comic archives downloaded with manga_downloader (also on github), and then insert that information into the archive using ComicTagger.

If existing tags match the ones extracted from the file name then the archive will not be updated. Currently only Comic Rack tags are recognised.

Options:
 * -a : Using this option will run the script in auto update mode, where files are automatically updated.

todo:
* Update the help to cover the switches
* Support existing tags other than Comic Rack
