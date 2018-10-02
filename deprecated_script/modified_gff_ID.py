import sys

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
    if line[0] == "#":
        file.write(line)
    else:        
        line = line.strip()
        if len(line) > 0:
            lines = line.split('\t')
            Scaffolds = lines[0].split("|")
            line = line.replace(lines[0], Scaffolds[3])
            file.write(line + '\n')
file.close()
fp.close()

