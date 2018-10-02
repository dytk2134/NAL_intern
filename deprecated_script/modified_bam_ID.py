import sys
import re

#filetype :  means gzip file, if empty means not gzip file
filetype = sys.argv[1]

filename=sys.argv[2]
output=sys.argv[3]

file = open(output,"w")
if filetype == "gz":
    import gzip
    fp = gzip.open(filename, "rb")
else:
    fp = open(filename,"r")

for line in fp:
    try:
        old_IDs = re.findall(u'gi\|\d*\|ref\|[a-zA-Z]{2}_[0-9]{9}\.\d\|', line)
        for old_ID in old_IDs:
            new_ID = old_ID.split("|")[3]
            line = line.replace(old_ID,new_ID)
        file.write(line)
    except AttributeError:
        file.write(line)
file.close()
fp.close()

