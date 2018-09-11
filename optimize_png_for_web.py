import sys
import argparse
import collections
from os import remove
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


def optimize_png(source_path, destination_path, quantization_blacklist):
    blacklist = set(quantization_blacklist)
    can_quantize = source_path.lower() not in blacklist
    _compress_png(source_path, destination_path, can_quantize)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='build a theme manifest')
    parser.add_argument('--unquantizable_textures', "-u", nargs='*', type=str, help='source yaml file path. E.g. manifest', required=True)
    parser.add_argument('--input', "-i", type=str, help='path to input png', required=True)
    parser.add_argument('--output', "-o", type=str, help='path to output png', required=True)
    args = parser.parse_args()

    optimize_png(args.input, args.output, args.unquantizable_textures)
