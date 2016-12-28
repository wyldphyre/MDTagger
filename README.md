MDTagger
========

A simple script to parse comic issue numbers and titles out of comic archives downloaded with the manga_downloader script (also on github), and then insert that information into the archive using ComicTagger.

If existing tags match the ones extracted from the file name then the archive will not be updated.

**Prerequisites**

* [ComicTagger](https://code.google.com/p/comictagger/ "Comic Tagger") for examing and updating the archive files

**Limitations**

* Currently only Comic Rack tags are recognised when examining archives, and only Comic Rack tags are inserted when updating archives.

**Options:**

* -a : Using this option will run the script in auto update mode, where files are automatically updated.

**todo:**

* Support detecting and inserting tags other than Comic Rack 
