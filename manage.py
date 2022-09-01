from src.converter import convert_files

import argparse

def main():
    parser = argparse.ArgumentParser(description='Convert Intan .rhd files to .eeg  and .egf files. Optionally, also convert a .csv file with position data in conjunction with a header .json file to a .pos file.')


    parser.add_argument('-o', '--output', help='Output directory to store .eeg, .egf and optional .pos files.', required=True)
    parser.add_argument('-i', '--rhd', help='Input path containing an .rhd file.', required=True)
    parser.add_argument('-p', '--csv', help='Input directory containing .csv file with position data.', required=False)
    parser.add_argument('-j', '--json', help='Input directory containing .json file with header.', required=False)

    args = parser.parse_args()

    convert_files(args.output, args.rhd, args.csv, args.json)

if __name__ == '__main__':
    main()
