#!/usr/bin/env python

import fontforge
import sys
import getopt

def deotfy(input,feature,script=None,language="dflt", verbose=False):
    output        = input
    lookups       = [ ]
    subtables     = [ ]

    for lookup in input.gsub_lookups:
        info = input.getLookupInfo(lookup)
        if info[0] == "gsub_single":
            for i in info[2]:
                if i[0] == feature:
                    if script:
                        for j in i[1]:
                            if j[0] == script:
                                for k in j[1]:
                                    if k == language:
                                        lookups.append(lookup)
                    else:
                        lookups.append(lookup)

    for lookup in lookups:
        for i in input.getLookupSubtables(lookup):
            subtables.append(i)

    for glyph in input.glyphs():
        for subtable in subtables:
            sub = glyph.getPosSub(subtable)
            if sub:
                target = sub[0][2]
                if verbose:
                    print "%s => %s" %(glyph.glyphname, target)
                output.selection.select(target)
                output.copy()
                output.selection.select(glyph.glyphname)
                output.paste()

    return output

def usage():
    message = """Usage: %s OPTION... FILE...

  -o, --output=FILE         file name of the resulting font
  -f, --feature=FEATURE     OpenType feature tag to be activated
  -s, --script=SCRIPT       optional OpenType script tag
  -l, --language=LANGUAGE   optional OpenType language tag
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

    infile   = None
    outfile  = None
    feature  = None
    script   = None
    language = None

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
            feature = a
        elif o in ("-s", "--script"):
            script = a
        elif o in ("-l", "--language"):
            language = a
        elif o in ("-v", "--verbose"):
            verbose = True

    if infile and outfile and feature:
        infont  = fontforge.open(infile)
        outfont = deotfy(infont, feature, script, language, verbose)
        outfont.generate(outfile)
    else:
        if not outfile:
            print "No output file specified"
        elif not feature:
            print "No feature specified"
        usage()
        sys.exit(2)

if __name__ == "__main__":
    main()
