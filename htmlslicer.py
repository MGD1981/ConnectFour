import pdb

def slice(self):
    """Main function called to slice the readable text from a file."""
    # pdb.set_trace()
    biglist = extractor(self).split()
    return biglist 

def extractor(biglist):
    """Runs a number of functions to clean html file 'biglist.'"""
    
    def _encloseclean(biglist, ca, cz, loc=0):
        """Removes text in 'biglist' enclosed by opening char combo  'ca' and
           closing char combo 'cz'."""
        print "Removing tags..."
        calen = len(ca)
        czlen = len(cz)
        newlist = []
        cc = 0
        while loc < len(biglist):
            if biglist[loc:(loc + calen)] == ca:
                cc += 1
            # Check if it's a comment; if so, don't add to cc until cz.
            if loc + 3 < len(biglist):
                if (biglist[loc] + biglist[loc+1] +
                    biglist[loc+2] + biglist[loc+3] == '<!--'):
                    while biglist[loc] != cz:
                        loc += 1
            if cc == 0:
                newlist.append(biglist[loc])
            if biglist[loc:(loc + czlen)] == cz:
                cc -= 1
            loc += 1
        return "".join(newlist)

    def _codereplace(biglist, chars, newchars, loc=0):
        """Replaces character combination 'chars' with replacement 'newchars'
        """
        print "Replacing encodings..."
        clen = len(chars)
        newlist = []
        while loc < len(biglist):
            if biglist[loc:(loc + clen)] == chars:
                loc += clen
                newlist.append(newchars)
            newlist.append(biglist[loc])
            loc += 1
        return "".join(newlist)

    def _coderemover(biglist, *chars):
        """Removes strings directly."""
        print "Deleting nonsense..."
        cyclesleft = len(chars)
        while cyclesleft > 0:
            biglist = _codereplace(biglist, chars[cyclesleft - 1], "")
            cyclesleft -= 1
        return biglist

    def _removefunk(biglist, *chars):
        """Removes words containing *chars.  Special exception made for '.'
           at the end of a word."""
        print "Scrapping non-words."
        loc = 0
        aloc = 0
        delword = False
        newlist = []
        while loc < len(biglist):
            if (len(set(biglist[loc]) & set(chars)) > 0 and
               (biglist[loc-1] != " " or biglist[loc+1] != " ")):
                delword = True
            if biglist[loc] == " ":
                if (not delword) or (biglist[loc-1] == '.'):
                    newlist.append(biglist[aloc:loc])
                delword = False
                aloc = loc 
            loc += 1
        return "".join(newlist)

    def _removeline(biglist, *chars):
        """Removes lines ending with any of the *chars."""
        print "Removing hidden code lines..."
        loc = 0
        lastn = 0
        newlist=[]
        while loc < len(biglist):
            if biglist[loc] == '\n':
                if len(set(chars) & set(biglist[loc-1])) == 0:
                    newlist.append(biglist[lastn:loc])
                lastn = loc
            loc += 1
        return "".join(newlist)
                



    # Call functions            
    biglist = _encloseclean(biglist, '<', '>')
    biglist = _encloseclean(biglist, '{', '}')
    biglist = _encloseclean(biglist, '[', ']')
    biglist = _encloseclean(biglist, '/*', '*/')
    biglist = _codereplace(biglist, '&#8217;', "'")
    biglist = _codereplace(biglist, '&#8220;', '"')
    biglist = _codereplace(biglist, '&#8221;', '"')
    biglist = _codereplace(biglist, '&nbsp;', " ")
    biglist = _coderemover(biglist, '&#8203;', '&#039;', '\xc2', '\xc3',
                                     '\xa0', '\xe2', '\x80', '\x99', '//' )
    biglist = _removefunk(biglist, '.', '#', '&', '@', '_', '|', '=')    
    biglist = _removeline(biglist, ';')


    # FUNCTIONS:
    # X) delete txt between param combos (modify 'extractor'?)
    # X) replace certain param combos with chars
    # ?) delete words containing params (and '.' unless at end)
    # ?) delete lines beginning/ending with params
    
    
    
                   
    return biglist
