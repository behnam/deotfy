#!/usr/bin/env python

import fontforge
import sys
import os
import getopt

def deotfy(input,features,scripts,languages,verbose=False):
    output        = input
    lookups       = [ ]
    subtables     = [ ]

    if not languages:
        languages = ["dflt"]

    for lookup in input.gsub_lookups:
        info = input.getLookupInfo(lookup)
        if info[0] == "gsub_single":
            for i in info[2]:
                if i[0] in features:
                    if scripts:
                        for j in i[1]:
                            if j[0] in scripts:
                                for k in j[1]:
                                    if k in languages:
                                        if verbose:
                                            print "Selected lookup: %s" % lookup
                                        lookups.append(lookup)
                    else:
                        if verbose:
                            print "Selected lookup: %s" % lookup
                        lookups.append(lookup)

    for lookup in lookups:
        for subtable in input.getLookupSubtables(lookup):
            if verbose:
                print "Selected subtable: %s" % subtable
            subtables.append(subtable)

    for glyph in input.glyphs():
        for subtable in subtables:
            sub = glyph.getPosSub(subtable)
            if sub:
                target = sub[0][2]
                if verbose:
                    print "Copying: %s => %s" %(glyph.glyphname, target)
                output.selection.select(target)
                output.copy()
                output.selection.select(glyph.glyphname)
                output.paste()

    return output

def usage():
    message = """Usage: %s OPTION... FILE...

Options:
  -o, --output=FILE         file name of the resulting font
  -f, --feature=FEATURE     OpenType feature tag to be activated
  -s, --script=SCRIPT       optional OpenType script tag
  -l, --language=LANGUAGE   optional OpenType language tag

  -h, --help                print this message and exit
  -v, --verbose             verbose mode
""" % sys.argv[0]

    print message

def main():
    try:
        opts, args = getopt.gnu_getopt(
                sys.argv[1:], "hvo:f:s:l:",
                ["help", "verbose",
                 "output=", "feature=", "script=", "language="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    infile = None
    outfile = None
    features = [ ]
    scripts = [ ]
    languages = [ ]

    verbose  = False

    if args:
        infile = args[-1]
    else:
        print "No input file"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-o", "--output"):
            outfile = a
        elif o in ("-f", "--feature"):
            features.append(a)
        elif o in ("-s", "--script"):
            scripts.append(a)
        elif o in ("-l", "--language"):
            languages.append(a)
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)

    if infile and outfile and features:
        infont  = fontforge.open(infile)
        outfont = deotfy(infont, features, scripts, languages, verbose)
        ext = os.path.splitext(outfile)[1]
        if ext in (".sfd", ".sfdir"):
            outfont.save(outfile)
        else:
            outfont.generate(outfile)
    else:
        if not outfile:
            print "No output file specified"
        elif not features:
            print "No feature specified"
        usage()
        sys.exit(2)

if __name__ == "__main__":
    main()
