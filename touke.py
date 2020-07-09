#coding: utf-8
import pickle
import argparse
import logging
import os
import subprocess
import sys
import json
from os import path

'''For hyld'''

def r2_getSections(so_path, out_path=None):
    cmd = 'rabin2.exe -S -j {}'.format(so_path)
    output = subprocess.check_output(cmd, shell=False).strip().decode("utf-8")
    if out_path:        
        with open(out_path, 'w') as f:
            f.write(json.dumps(json.loads(output), indent=4))
    print(output)

def r2_getSections_json(so_path):
    cmd = 'rabin2.exe -S -j {}'.format(so_path)
    output = subprocess.check_output(cmd, shell=False).strip().decode("utf-8")
    if output:        
        return json.loads(output)
    return None

def r2_getSections_print(so_path):
    cmd = 'rabin2.exe -S {}'.format(so_path)
    output = subprocess.check_output(cmd, shell=False).strip().decode("utf-8")
    print(output)

def tuoke_sosection(so_bytes, section_file, name, offset):    
    with open(section_file, 'rb') as f2:
        print(f'tuoke {name}')
        sec_bytes = f2.read()
        for i, b in enumerate(sec_bytes):
            so_bytes[offset+i] = b
    return so_bytes

def tuoke_sofile(org_sofile, out_path, sections = ['.text', '.data']):
    base_name = os.path.basename(org_sofile)
    new_sofile = f'{out_path}/hack/jm_{base_name}'
    section_infos = r2_getSections_json(org_sofile)
    so_bytes = []
    with open(org_sofile, 'rb') as f1:
        so_bytes = list(f1.read())
    
    for e in section_infos['sections']:
        sec = e['name']
        sec_file_path = f'{out_path}/hack/{sec}'            
        offset = e['vaddr']
        if sec in sections and os.path.isfile(f'{sec_file_path}'):                
            so_bytes = tuoke_sosection(so_bytes, f'{sec_file_path}', sec, offset)
        # else:
        #     print(f'path not exist {sec_file_path}')

    with open(new_sofile, 'wb') as f2:
        f2.write(bytes(so_bytes))

def pull_sections(out_path):
    cmd = f'adb pull /sdcard/hack/ {out_path}'
    output = subprocess.check_output(cmd, shell=False).strip().decode("utf-8")
    print(output)

def clear_sections():
    cmd = f"adb shell su -c 'rm -rf /sdcard/hack/*'"
    output = subprocess.check_output(cmd, shell=False).strip().decode("utf-8")
    print(output)

def main():
    """ This function is where the magic happens.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--so-path', help="so file", required=False)
    parser.add_argument('-o', '--out-path', help="out file", required=False)
    parser.add_argument('-p', help="pull data",  action="store_true", required=False)
    parser.add_argument('-c', help="clear data",  action="store_true", required=False)
    parser.add_argument('-s', help="section data",  action="store_true", required=False)
    parser.add_argument('-i',  action="store_true", required=False)

    ops = parser.parse_args()
    print(ops)
    
    if ops.p:
        pull_sections(ops.out_path)
    elif ops.c:
        clear_sections()
    elif ops.s:
        r2_getSections_print(ops.so_path)
    else:
        tuoke_sofile(ops.so_path, ops.out_path)

if __name__ == "__main__":
    main()
