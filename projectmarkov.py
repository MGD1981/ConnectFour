import pdb
import urllib
import htmlslicer


print "\nPlease enter a URL:"
u = raw_input(">> ")
if len(u) < 1:
    u = 'http://www.thefatalistmarksman.com/'
print "\nPlease be patient as we retrieve web content...\n"
f = urllib.urlopen(u, 'r')
s = f.read()
f.close()

#pdb.set_trace()
slicedcontent = htmlslicer.slice(s) 
print slicedcontent

