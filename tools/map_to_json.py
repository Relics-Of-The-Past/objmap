import json
import oead
import pathlib
import sys

def get_files(dir):
    files = []
    if not isinstance(dir, pathlib.Path):
        dir = pathlib.Path(dir)

    for sub in dir.iterdir():
        if sub.is_dir():
            files.extend(get_files(sub))
        else:
            files.append(sub)
    return files

def check_compression(data):
    if ''.join(oead.yaz0.get_header(data).magic) == 'Yaz0':
        data_out = oead.yaz0.decompress(data)
    else:
        data_out = data
        print('File was not Yaz0 compressed')
    return data_out

def get_dir(data_dir) -> pathlib.Path:
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def check_data_types(valIn):
    valOut = None
    try:
        valOut = oead.byml.get_bool(valIn)
    except:
        try:
            valOut = oead.byml.get_double(valIn)
        except:
            try:
                valOut = oead.byml.get_float(valIn)
            except:
                try:
                    valOut = oead.byml.get_int(valIn)
                except:
                    try:
                        valOut = oead.byml.get_int64(valIn)
                    except:
                        try:
                            valOut = oead.byml.get_string(valIn)
                        except:
                            try:
                                valOut = oead.byml.get_uint(valIn)
                            except:
                                try:
                                    valOut = oead.byml.get_uint64(valIn)
                                except:
                                    valOut = None
    return(valOut)

def expand_data(data):
    output_dict = {}
    output_list = []
    if isinstance(data, oead.byml.Hash) or isinstance(data, dict):
        for key in dict(data).keys():
            output_dict.update({key: expand_data(data[key])})
        return output_dict
    elif isinstance(data, oead.byml.Array) or isinstance(data, list):
        for entry in data:
            output_list.append(expand_data(entry))
        return(output_list)
    else:
        return check_data_types(data)

def convert_to_json(file_path, output_path):
    map_type = file_path.parts[-3]
    field_area = file_path.name.split('_')[0]
    save_dir = get_dir(pathlib.Path(f'{output_path}/{map_type}/{field_area}'))
    with open(file_path, 'rb') as read_file:
        decompressed = check_compression(read_file.read())
    try:
        data = oead.byml.from_binary(decompressed)
    except Exception as e:
        print(e)
        return
    with open(save_dir / f'{file_path.name.split(".")[0]}.json', 'wt') as save_file:
        print(f'Saving data from {file_path.name} to {save_file.name}')
        save_file.write(json.dumps(expand_data(data), indent=2))

def main(args: list):
    files = get_files(args[1])
    for file in files:
        convert_to_json(file, args[2])

if __name__ == '__main__':
    main(sys.argv)