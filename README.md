# wordlist-knife: your illiterate friend

Tool for merging, subtracting and generating wordlists.

## Why was it made?

When faced with the plethora for wordlists in [SecLists][SecLists], I
found it overwhelming and so stick to the few lists that I have
been lucky with.

It is often not clear which wordlists are super/sub wordlists of
others. Worse, many of the wordlists are disjoint, but contain many
1000's of identical entries. Thus, if just trying another wordlist
either it is needed to waste time filtering them (e.g. with `grep
-Fvxf`, but only to find one wordlist had `/` prepended to each entry,
so its needed to use `sed` too) or just run with the larger wordlist
and accept time is wasted.

Further, adding entries to wordlists is also a pain. The choices are:

1. Maintain separate wordlists and concatenate them before using
   (e.g. with `bash` process substitution). Alas, this just adds
   complexity to commands.

2. Create branch of SecLists and edit wordlists directly, then rebase
   `branch` instead of `pull`ing so its clear what words you have
   added over time.
   
3. Just do it adhock.

Finally, using standard command line tools for processing wordlists is
fine for one-off operations. However, when doing this many times it
obfuscates what is really happening on the command line and wastes
time on repetitive tasks. For example, a typical first scan of an
`apache` server I might run is as follow:

```
$ grep -ve '^/\.ht' quickhits.txt | ffuf -w - -u http://xyz/FUZZ
```

However, then the second scan could be (notice the regex also
changed):

```
$ grep -ve '^\.ht' raft-files-small.txt | ffuf -w - -u http://xyz/FUZZ
```


This tool aims to remove lots of the pain of using wordlists as
described above. At a high level, it reads a bunch or wordlists,
removes duplicate entries (possibly mangles them, e.g. like `sed`) and
prints them out. Further more, it is possible to define composite
wordlists in a config file can easily be referenced by a friendly
name.

Thus, its easy to get some understanding how related two wordlists are
by just subtracting one wordlist from another (or many others) and
viewing the results. This is useful for getting some understanding
about the content of different wordlists.

However, the real advantage to the tool is when using the config file
to setup pre-defined lists. Each of these lists could further consist
of a number of other lists, mangled (i.e. placing words into a normal
form, like removing leading slashes or comments), de-duplicated, and
finally filtered by either other lists or a regex.


## Installation

There are no special dependencies required. So a simple `pip install wordlist-knife` is
all that is needed.

## Examples

[See command line args](#usage). 

### Checking for duplicates in wordlist

Often this is a mark of quality of how well a wordlist was put
together.

```
$ diff raft-large-directories.txt <(wlk raft-large-directories.txt)
48562d48561
< index
59093,59094d59091
< G
< ļ
```

Sometimes it is required to specify the encoding:

```
$ md5sum  rockyou.txt <(wlk --encoding latin1 rockyou.txt)
9076652d8ae75ce713e23ab09e10d9ee  rockyou.txt
9076652d8ae75ce713e23ab09e10d9ee  /dev/fd/63
```

The size of rockyou will take a few seconds to fully check for
duplicates. However, it will start printing checked lines immediately
as there is no need to sort it.

### Entries in one wordlist that are not in the other.

Useful in cases where you have already used the first wordlist and
want to quickly check another wordlist without repeating the work
done, or you are just interested in the difference of two with a
similar name.

```
$ wlk raft-large-directories-lowercase.txt --filters raft-large-directories.txt | wc -l
4079
```

Possible to concatenate multiple lists first and then check:

```
$ wlk directory-list-2.3-medium.txt directory-list-2.3-small.txt --filter directory-list-2.3-big.txt 'regex:^#.*$'
```

Here a regex is used to also filter comments from the output. This
regex is also hardcoded and could have been given as:

```
$ wlk directory-list-2.3-medium.txt directory-list-2.3-small.txt --filter directory-list-2.3-big.txt save:comments
```

### Wordlist generation

Support for quickly generating permutations of a *small* number of
words is provided. This is useful for generating possible combinations
of first and last names, names of companies.

So for a user `j bloggs` the following could be generated:

```
$ wlk fancy:/j/bloggs --fancy-concat . --fancy-no-empty --filter list:/J.BLOGGS/bloggs.J
j
J
bloggs
BLOGGS
Bloggs
j.bloggs
j.BLOGGS
j.Bloggs
J.bloggs
J.Bloggs
bloggs.j
BLOGGS.j
BLOGGS.J
Bloggs.j
Bloggs.J
```

Notice, here also two items are explicitly removed from the list for
demonstration purposes of the `list` syntax.

Currently only capitalisation of the base words are varied. However,
the possibilities quickly blow up exponentially, so its advisable to
keep the number of words low and limit the number of chars passed to
`--fancy-concat` based on the context.


It is also possible to combine generated wordlists into existing
lists. For example to include a company name into a wordlist used for
fuzzing:

```
$ wlk fancy:/company/name directory-list-2.3-small.txt
```

The output of this could be piped to the application or via process
substitution.

### Mangle lists (i.e. apply `sed` like modifications)

There are occasions where its handy to tweak entries in a
wordlist. The following is an example where it both mangles any php
file to search for temporary backup files and then filters the list to
only select words with php in.

```
$ wlk list:/index.php/123/def/isphpok.txt --manglers 'subst:/^([^.]+)\.php/#\1.php#' --filter 'regex:^(?!.*php)'
#index.php#
isphpok.txt
```

In addition, there is also an `upper` and `lower` mangle that does a
simple upper or lower case operation on the word.

Other manglers, such as urlencode, base64, computing digests have not
been implemented.

### Saved lists

Typically, only a few lists are used regularly. It is possible to
create aliases for these lists in `~/.wordlist-knife`. In fact, its
possible to define lists that are aggregated, filtered and mangled in
this file. 

For example, if there is a wordlist that is used lots but needs some
additional items its possible to define the list in this file with a
few extra items appended to it, or a filter applied or even mangled.

The format of this file is `json`. As an example of this applied to
the `quickhits.txt` file (see [SecLists][SecLists]) could be as
follows:

```json
{
  "quick": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/quickhits.txt"
    ],
    "manglers": [
      "subst:|^/|"
    ],
    "filters": [],
    "desc": "quickhits.txt with leading slashes stripped"
  }
}
```

Here, `wordlists`, `filters` and `manglers` follow the same convention
as when passed on the command line. With the difference, when passed
on the command line they are applied globally, when defined here they
are only applied to the wordlist being defined. The `desc` is
optional, and displayed in the help.

Then its possible use this defined list as follows:

```
$ wlk save:quick
```

A major advantage of this is that it greatly simplifies management of
wordlists. Especially when using 3rd party ones, such as from
[SecLists][SecLists]. Before I would create my own git commits with
custom tweaks in the files that I have found useful, however this
would require rebaseing the repo from time to time. In addition, it is
needed to remember the full name file and path of the repo, and then
often filter the wordlist through `grep` to remove undesirable
lines. Saving these configurations into a config file with names that
are meaningful to myself greatly reduces the burden.


### Full example

Within my config file, I define a number of wordlists that dont
overlap and are aggregates of standard wordlists. This means its
possible to use smaller wordlists before going to larger ones. When
using the larger ones, I dont waste time repeating already used words
(or remembering names of lesser  wordlist or typing paths):

```
$ wlk save:dir1 --filt save:apache | ffuf -w - -u http://xyz/FUZZ
```

or with files too:

```
$ wlk save:dir1 save:files1 --filt save:apache | ffuf -w - -u http://xyz/FUZZ
```


Then, if there is nothing of interest run a larger scan:

```
$ wlk save:dir2 --filt save:apache | ffuf -w - -u http://xyz/FUZZ
```


As an example of a config file that is based off wordlists available
from [SecLists][SecLists], see below. It makes use of many of the
features:

```json
{
  "tomcat": {
      "filters": [
          "regex:[\\[\\]]"
      ]
  },
  "dir0": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/raft-small-directories.txt",
      "/path/to/SecLists/Discovery/Web-Content/raft-small-directories-lowercase.txt",
      "list:|cgi-bin/"
    ],
    "desc": "raft-directories-words.txt + raft-small-directories-lowercase.txt"
  },
  "dir1": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/raft-large-directories.txt",
      "/path/to/SecLists/Discovery/Web-Content/raft-large-directories-lowercase.txt",
      "list:,.hg"
    ],
    "filters": [
      "save:dir0"
    ],
    "desc": "raft-large-directories.txt + raft-large-directories-lowercase.txt | filtered by dir0"
  },
  "dir2": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt",
      "/path/to/SecLists/Discovery/Web-Content/directory-list-lowercase-2.3-big.txt"
    ],
    "filters": [
      "save:comments",
      "save:dir0",
      "save:dir1",
      "regex:%0[aAdD]"
    ],
    "desc": "directory-list-2.3-big.txt | filtered by dir0 and dir1"
  },
  "file0": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/raft-small-files.txt",
      "/path/to/SecLists/Discovery/Web-Content/raft-small-files-lowercase.txt"
    ],
    "desc": "raft-small-files.txt + raft-small-files-lowercase.txt"
  },
  "file1": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/raft-large-files.txt",
      "/path/to/SecLists/Discovery/Web-Content/raft-large-files-lowercase.txt",
      "list:,composer.json,vendor/composer/installed.json"
    ],
    "filters": [
      "save:file0"
    ],
    "desc": "raft-large-files.txt + raft-large-files-lowercase.txt | filtered by file0"
  },
  "file2": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/common-and-french.txt",
      "/path/to/SecLists/Discovery/Web-Content/PHP.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/common-and-spanish.txt",
      "/path/to/SecLists/Discovery/Web-Content/IIS.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/CGI-XPlatform.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/common-and-italian.txt",
      "/path/to/SecLists/Discovery/Web-Content/CGIs.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/ascx.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/asp.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/aspx.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/cfm.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/cpp.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/css.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/cs.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/c.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/html.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/jar.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/java.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/jspf.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/jsp.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/js.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/php3.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/php5.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/phpt.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/php.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/pl.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/py.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/rb.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/sh.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/swf.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/tpl.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/vb.txt",
      "/path/to/SecLists/Discovery/Web-Content/SVNDigger/cat/Language/wsdl.txt",
      "/path/to/SecLists/Discovery/Web-Content/CommonBackdoors-ASP.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/CommonBackdoors-JSP.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/CommonBackdoors-PHP.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/CommonBackdoors-PL.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/Common-DB-Backups.txt",
      "/path/to/SecLists/Discovery/Web-Content/Common-PHP-Filenames.txt",
      "/path/to/SecLists/Discovery/Web-Content/Logins.fuzz.txt",
      "/path/to/SecLists/Discovery/Web-Content/Roundcube-123.txt"
    ],
    "filters": [
      "save:comments",
      "save:dir0",
      "save:dir1",
      "save:dir2",
      "save:file0",
      "save:file1",
      "regex:/$",
      "regex:%0[aAdD]"
    ],
    "manglers": [
      "subst:/\\?.*$/",
      "subst:|^/|"
    ],
    "desc": "assorted selection of filenames from SecLists/Discovery/Web-Content"
  },
  "quick": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/quickhits.txt",
      "list:,robots.txt,~root/,cgi-bin/,sitemap.xml"
    ],
    "manglers": [
      "subst:|^/|"
    ],
    "desc": "quickhits.txt with leading slashes stripped"
  },
  "words": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/raft-large-words.txt",
      "/path/to/SecLists/Discovery/Web-Content/raft-large-words-lowercase.txt",
      "list:,.hg"
    ],
    "desc": "raft-large-words.txt + raft-large-words-lowercase.txt"
  },
  "dir": {
    "wordlists": [
      "save:dir0",
      "save:dir1"
    ],
    "desc": "raft-large-directories.txt + raft-large-directories-lowercase.txt, i.e. dir0 and dir1"
  },
  "file": {
    "wordlists": [
      "save:file0",
      "save:file1"
    ],
    "desc": "raft-large-files.txt + raft-large-files-lowercase.txt, i.e. file0 and file1"
  },
  "dns": {
    "wordlists": [
      "/path/to/SecLists/Discovery/DNS/subdomains-top1million-20000.txt"
    ],
    "filters": [
      "list:/gc._msdcs/#www/#mail/_domainkey"
    ]
  },
  "dark-1k": {
    "wordlists": [
      "/path/to/SecLists/Passwords/darkweb2017-top1000.txt"
    ]
  },
  "dark-10k": {
    "wordlists": [
      "/path/to/SecLists/Passwords/darkweb2017-top10000.txt"
    ]
  },
  "params": {
    "wordlists": [
      "/path/to/SecLists/Discovery/Web-Content/burp-parameter-names.txt"
    ]
  },
  "names": {
    "wordlists": [
      "/path/to/SecLists/Usernames/xato-net-10-million-usernames-dup.txt"
    ]
  }
}
```

## Usage

```
$ wlk -h         
usage: wlk [-h] [--filters FILT [FILT ...]] [--manglers MNGL [MNGL ...]]
           [--encoding ENC] [--fancy-no-empty-concat]
           [--fancy-concat-chars FANCY_CHARS]
           LIST [LIST ...]

  Tool for mangling wordlists. Works by reading in one ore more source
wordlists, removing duplicates entries and then filtering the words. When the
words are output, the original order is preserved (with exception of removed
entries). Also has support for basic wordlist generation from keywords.

  Can be used in number of ways from merging wordlists, or just appending new
words to an existing wordlist, filtering existing wordlists or supplementing
wordlists with keywords (and some derivations).

  Currently there is no support for sorting, as its often preferable to have
wordlists start with common words.

positional arguments:
  LIST                  Source wordlists. These must occur before the "--
                        filters" argument, if used, otherwise argparse can not
                        determine where the parameters belong. These arguments
                        can be paths to wordlist files or specifications of
                        wordlists to generate.
                        
                        Each argument is processed as follows: First, it is
                        check to determine if its a file that can be opened. If
                        so, its opened and the lines are used. Otherwise it
                        will be interpreted as "tag:value" where the tag
                        determines the meaning of the value. The following tags
                        are supported:
                        
                        * save: Pre-configured lists, e.g. save:apache. These
                        are either hardcoded (such as apache) and typically for
                        use with with --filters, or read from the ~/.wordlist-
                        knife file as aliases for wordlist paths. This file
                        should be json, see
                        https://github.com/kazkansouh/wordlist-knife for an
                        example.
                        
                        * fancy: Generate variants of list with
                        upper/lower/title cases. Same format as list. Useful
                        for deriving a number of words from a small number of
                        known words, e.g. a company name or a person. Given as:
                        "fancy:/jo/bloggs" to generate variants.
                        
                        * list: Define constant list, first char is delimiter.
                        e.g. list:/abc/123. Useful for quickly adding/removing
                        a few words to a wordlist.
                        
                        * file: Read a wordlist file from path.
                        
                        
                        The following lists are predefined (i.e. for use with
                        save):
                        
                        * file: raft-large-files.txt + raft-large-files-
                        lowercase.txt, i.e. file0 and file1
                        
                        * dir: raft-large-directories.txt + raft-large-
                        directories-lowercase.txt, i.e. dir0 and dir1
                        
                        * words: raft-large-words.txt + raft-large-words-
                        lowercase.txt
                        
                        * quick: quickhits.txt with leading slashes stripped
                        
                        * file2: assorted selection of filenames from
                        SecLists/Discovery/Web-Content
                        
                        * file1: raft-large-files.txt + raft-large-files-
                        lowercase.txt | filtered by file0
                        
                        * file0: raft-small-files.txt + raft-small-files-
                        lowercase.txt
                        
                        * dir2: directory-list-2.3-big.txt | filtered by dir0
                        and dir1
                        
                        * dir1: raft-large-directories.txt + raft-large-
                        directories-lowercase.txt | filtered by dir0
                        
                        * dir0: raft-directories-words.txt + raft-small-
                        directories-lowercase.txt
                        
                        * comments: ^#.*$ (regex)
                        
                        * apache: (^|/)\.ht (regex), ^\.php[34567]?$ (regex),
                        \.phps$ (regex)
                        

optional arguments:
  -h, --help            show this help message and exit
                        
  --filters FILT [FILT ...]
                        Items of the filter argument are removed from the
                        source wordlists. Each filter follows the same rules as
                        the wordlists, i.e. can be a file or specified with a
                        tag.
                        
                        However, in addition, it also supports the "regex" tag
                        that filters the words based on a given regex. E.g.
                        "regex:\.phps$".
                        
  --manglers MNGL [MNGL ...]
                        Mangle (i.e. mutate) words. Each mangler is applied in
                        order given on command line.
                        
                        The following manglers are supported:
                        
                        * subst: Regex substitution, first char is delimiter.
                        e.g. to prefix php pages with "x_" the following could
                        be used: "subst:/^([^.]+)\.php/x_.php".
                        
                        * lower: Convert words to lowercase.
                        
                        * upper: Convert words to uppercase.
                        
  --encoding ENC        Specify the encoding to use for io. E.g. when using
                        rockyou.txt it is required to set this to latin1.
                        (default: utf8).
                        
  --fancy-no-empty-concat
                        Disable joining words with the empty string for fancy.
                        
  --fancy-concat-chars FANCY_CHARS
                        List of chars to use for joining words for fancy.
                        (default: -_)
                        

  wordlist-knife v0.0.1. Copyright (C) 2020 Karim Kanso. All Rights Reserved.
```

# Other bits

Copyright 2020, Karim Kanso. All rights reserved. Project licensed under GPLv3.

[SecLists]: https://github.com/danielmiessler/SecLists "GitHub.com: SecLists"
[git]: https://github.com/kazkansouh/wordlist-knife "GitHub.com: wordlist-knife"
[pypi]: https://pypi.org/project/wordlist-knife/ "PyPI: wordlist-knife"
