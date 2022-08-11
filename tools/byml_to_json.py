import byml
import sys
import json
import oead

with open(sys.argv[1], 'rb') as read_file:
    data = byml.Byml(oead.yaz0.decompress(read_file.read())).parse()
    print(data)

with open(sys.argv[2], 'wt') as write_file:
    write_file.write(json.dumps(data, indent=2))
    print('saved')
