import json 
import sys
try:
    json.loads(open(sys.argv[1]).read())
except:
    exit(1)
exit(0)
