import sys
import argparse
import collections
from os import remove, path
from subprocess import call


def _compress_png(source_path, destination_path, is_quantization_allowed):
    PNG_CRUSH_TOOL = "./lib/pngcrush_1_8_11_w64.exe"
    PNG_QUANT_TOOL = "./lib/pngquant.exe"
    png_crush_source = source_path
    temporary_file = None

    if is_quantization_allowed:
        temporary_file = source_path + ".quant"
        call([PNG_QUANT_TOOL, "--strip", "--quality=45-75", "--speed", "1", source_path, "-o", temporary_file])
        png_crush_source = temporary_file
    
    call([PNG_CRUSH_TOOL, "-rem", "alla", "-rem", "text", "-reduce", "-q", png_crush_source, destination_path])

    if temporary_file:
        remove(temporary_file)


def optimize_png(source_path, destination_path, quantization_blacklist_path):
    with open(quantization_blacklist_path, 'r') as f:
        blacklist = set(f.read().split())

    prev_blacklist_path = quantization_blacklist_path + ".prev"
    prev_blacklist = set()
        
    if path.isfile(prev_blacklist_path):
        with open(prev_blacklist_path, 'r') as f:
            prev_blacklist = set(f.read().split())


    can_quantize = source_path.lower() not in blacklist
    quantized_last_time = source_path.lower() not in prev_blacklist if len(prev_blacklist) else can_quantize
    
    if not path.isfile(destination_path) or \
            path.getmtime(source_path) > path.getmtime(destination_path) or \
            can_quantize != quantized_last_time:
        _compress_png(source_path, destination_path, can_quantize)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='optimize a png file for the web')
    parser.add_argument('--unquantizable_textures', "-u", help='path to file with a list of unquantizable textures', required=True)
    parser.add_argument('--input', "-i", type=str, help='path to input png', required=True)
    parser.add_argument('--output', "-o", type=str, help='path to output png', required=True)
    args = parser.parse_args()

    optimize_png(args.input, args.output, args.unquantizable_textures)
