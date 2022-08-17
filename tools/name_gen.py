from wildbits._sarc import *
from pymsyt import Msbt
import oead
import time
import pathlib
import sys
import json

class Bootup_Msg:
    def __init__(self, bootupPath):
        self.bootupPath = pathlib.Path(bootupPath)
        self.region = self.bootupPath.name.rstrip('.pack').split('_')[1][:2]
        self.language = self.bootupPath.name.rstrip('.pack').split('_')[1][2:]
        self.sarc, self.sarcTree, self.moddedFiles = open_sarc(self.bootupPath)
        self.textFiles =  self.sarcTree['Message'][f'Msg_{self.region}{self.language}.product.ssarc']
        self.startTime = time.time()

    def readFile(self, fileName):
        startTime = time.time()
        fileData = get_nested_file_data(self.sarc, fileName)
        big_endian = fileData[0x08:0x0A] == b"\xfe\xff"
        msbtBinData = Msbt.from_binary(fileData)
        msbtData = msbtBinData.to_dict()
        functionTime = time.time() - startTime
        return msbtData

    def get_actor_names(self, file_name):
        file_path = f'Message/Msg_{self.region}{self.language}.product.ssarc//ActorType/{file_name}'
        file_data = self.readFile(file_path)
        names = {}
        for entry in file_data['entries'].keys():
            if (entry.split('_')[-1] == 'Name'):
                name_data = file_data['entries'][entry]['contents']
                for sub in name_data:
                    if ('text' in sub.keys()):
                        names.update({entry.rstrip('_Name'): sub['text'].replace('\u2019', "'")})
                    else:
                        continue
            else:
                continue
        return names

    def getTotalElapsedTime(self):
        elapsedTime = time.time() - self.startTime
        return str(f'Total Elapsed Time: {elapsedTime} seconds')

def main(bootup_path, output_path):
    bootup = Bootup_Msg(bootup_path)
    master_names = {}
    for file in bootup.textFiles['ActorType']:
        master_names.update(bootup.get_actor_names(file))
    with open(output_path, 'wt') as write_names:
        write_names.write(json.dumps(master_names, indent=2))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])