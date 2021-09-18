# MDTagger

A simple script to parse comic issue numbers and titles out of comic archives filenames, and then insert that information into the archive using ComicTagger.

If existing tags match the ones extracted from the file name then the archive will not be updated.

## Prerequisites

- [ComicTagger](https://code.google.com/p/comictagger/ "Comic Tagger") for examining and updating the archive files

## Limitations

- Currently only Comic Rack tags are recognised when examining archives, and only Comic Rack tags are inserted when updating archives.

## Command Line Options

- `-a` : Using this option will run the script in auto update mode, where files are automatically updated.

## To Do

- Really need to overhaul the filename parsing to be more reliable and to be able to cope with more scenarios
