#!/usr/bin/env python

import sys
import getopt

def match_er(fd, er, start=0):

    # move to location
    loc = start
    fd.seek(loc, 0)

    s = 0
    sz = len(er)

    byte = fd.read(1)
    while byte != "":
        if byte == er[s]:
            s += 1
        else:
            s = 0

        if s == sz:
            return loc-sz+1

        loc += 1
        byte = fd.read(1)
    return -1

def copy_file(fd, to, loc, sz):
    f = open(to, 'wb')
    fd.seek(loc, 0)
    for i in range(sz):
        byte = fd.read()
        if byte == "":
            break
        f.write(byte)
    f.close()

def head_trail(fname, header, trailer, prefix, suffix):
    fd = open(fname, 'rb')
    num = 0

    loc = match_er(fd, header)
    while loc > 0:
        t_loc = match_er(fd, trailer, loc)

        if loc > 0:
            copy_file(fd, prefix + str(num) + suffix, loc, t_loc - loc)
            num += 1
        else:
            break

        loc = match_er(fd, header, loc+1)

    fd.close()
    return num

def JPG_JFIF(fname): 
    return head_trail(fname, '\xff\xd8\xff\xe0', '\xff\xd9', "filejfif", ".jpg")

def JPG_JFIFF(fname): 
    return head_trail(fname, '\xff\xd8\xff\xe8', '\xff\xd9', "filejfiff", ".jpg")

def JPG_EXIF(fname): 
    return head_trail(fname, '\xff\xd8\xff\xe1', '\xff\xd9', "fileexif", ".jpg")

def JPG(fname):
    print "Searching for JPG images"
    num = 0
    num += JPG_JFIF(fname)
    num += JPG_EXIF(fname)
    num += JPG_JFIFF(fname)
    print "Found %d potential JPG files" % (num)

def PNG(fname):
    print "Searching for PNG images"
    num = head_trail(fname, '\x89\x50\x4e\x47\x0d\x0a\x1a',
                            '\x49\x45\x4e\x44\xae\x42\x60\x82', "file", ".png")
    print "Found %d potential PNG files" % (num)

def GIF(fname):
    print "Searching for GIF images"
    num = 0
    num += head_trail(fname, '\x47\x49\x46\x38\x37\x61',
                            '\x00\x3b', "file87a", ".gif")
    num += head_trail(fname, '\x47\x49\x46\x38\x39\x61',
                            '\x00\x3b', "file89a", ".gif")
    print "Found %d potential GIF files" % (num)

def BMP(fname):
    print "Searching for BMP images"
    header = '\x42\x4d'
    fd = open(fname, 'rb')

    num = 0
    prefix = "file"

    loc = match_er(fd, header)
    while loc > 0:
        fd.seek(loc, 0)
        for i in range(len(header)):
            fd.read(1)

        # read size
        byte0 = fd.read(1)
        byte1 = fd.read(1)
        byte2 = fd.read(1)
        byte3 = fd.read(1)

        sz = 255**3 * ord(byte3) + 255**2 * ord(byte2) +\
                255 * ord(byte1) + ord(byte0)

        # check size is reasonable
        if sz < 10000000:
            copy_file(fd, prefix + str(num) + '.bmp', loc, sz)
            num += 1

        loc = match_er(fd, header, loc+1)

    fd.close()
    print "Found %d potential BMP files" % (num)

def usage():
    print "Usage:\n%s [OPTIONS]" % (sys.argv[0])
    print ""
    print "OPTIONS:"
    print "   -f <filename>      File to search through (required)"
    print "   --file=<filename>"
    print "   -a, --all          Look for all known formats"
    print "   -b, --bmp          Look for BMPs"
    print "   -j, --jpg          Look for JPGs"
    print "   -p, --png          Look for PNGs"
    print "   -g, --gif          Look for GIFs"

def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:abjpg",
                    ['help',
                     'file=',
                     'all',
                     'bmp',
                     'jpg',
                     'png',
                     'gif',
                    ])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    # Check for help and exit
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(1)

    fname = None

    # Ensure file name is provided and works
    for o, a in opts:
        if o in ('-f', '--file'):
            fname = a
            try:
                fd = open(fname, 'r')
                fd.close()
            except:
                print "File %s not found" % (fname)
                sys.exit(2)

    # Check for filetype searches
    if fname is not None:
        for o, a in opts:
            if o in ('-a', '--all'):
                BMP(fname)
                JPG(fname)
                PNG(fname)
                GIF(fname)
            if o in ('-b', '--bmp'):
                BMP(fname)
            if o in ('-j', '--jpg'):
                JPG(fname)
            if o in ('-p', '--png'):
                PNG(fname)
            if o in ('-g', '--gif'):
                GIF(fname)
    else:
        print "Must supply a filename"
        sys.exit(2)

if __name__ == '__main__':
    main()
