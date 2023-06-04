#!/usr/bin/env python3
"""Fix bib files sort order and other stuff."""

import sys
from argparse import ArgumentParser, FileType


def main():
    '''CLI handling.'''
    bibs = {}
    ap = ArgumentParser()
    ap.add_argument('-i', '--input', required=True, type=open,
                    help='read bib from INFILE')
    ap.add_argument('-o', '--output', required=True, type=FileType('w'),
                    help='write to OUTFILE')
    options = ap.parse_args()
    in_atblock = False
    in_value = False
    current_id = None
    current_key = None
    current_value = None
    current_bracket = None
    bracket_stack = 0
    for line in options.input:
        if not in_atblock and not in_value:
            if '@' in line:
                in_atblock = True
                fields = line.strip().split('{')
                current_id = fields[1].rstrip(',').lower()
                bibs[current_id] = {'@type': fields[0]}
            elif line.strip() != '':
                print(line.strip(), file=options.output)
        elif in_atblock and not in_value:
            if '=' in line:
                fields = line.split('=', 1)
                key = fields[0].strip()
                current_key = key
                value = fields[1].strip()
                if value.startswith('{') and \
                        value.count('{') == value.count('}'):
                    bibs[current_id][key] = \
                        value.lstrip('{').rstrip(',').rstrip('}')
                elif value.startswith('"') and value.endswith('",'):
                    bibs[current_id][key] = value.lstrip('"').rstrip('",')
                elif value.startswith('"') and value.endswith('"'):
                    bibs[current_id][key] = value.lstrip('"').rstrip('"')
                elif not value.startswith('{') and not value.startswith('"'):
                    bibs[current_id][key] = value.rstrip(',')
                elif value.startswith('{'):
                    in_value = True
                    current_bracket = '{'
                    current_value = value.lstrip('{')
                    bracket_stack = value.count('{') - value.count('}')
                elif value.startswith('"'):
                    in_value = True
                    current_bracket = '"'
                    current_value = value.lstrip('"')
                else:
                    bibs[current_id][key] = value.rstrip(',')
            elif '}' in line:
                in_atblock = False
                current_id = None
        elif in_atblock and in_value:
            value = line.strip()
            if current_bracket == '{' and \
                    value.count('}') == value.count('{') + bracket_stack:
                current_value += ' ' + value.rstrip(',').rstrip('}')
                bibs[current_id][current_key] = current_value
                in_value = False
                current_bracket = None
            elif current_bracket == '"' and value.endswith('",'):
                current_value += ' ' + value.rstrip('",')
                bibs[current_id][current_key] = current_value
                in_value = False
                current_bracket = None
            elif current_bracket == '"' and value.endswith('"'):
                current_value += ' ' + value.rstrip('"')
                bibs[current_id][current_key] = current_value
                in_value = False
                current_bracket = None
            elif current_bracket == '{':
                bracket_stack += value.count('{') - value.count('}')
                current_value += ' ' + value.strip()
            else:
                current_value += ' ' + value.strip()
        else:
            print('parse state error: in value but not in at block',
                  file=sys.stderr)
            sys.exit(1)
    print('# rest of the file is automatically fixed by a python script',
          file=options.output)
    for iidee, bib in sorted(bibs.items()):
        print(file=options.output)
        print(f'{bib["@type"]}{{{iidee},', file=options.output)
        for key, value in sorted(bib.items()):
            if key == '@type':
                continue
            if len(key) + len(value) < 72:
                print(f'    {key} = {{{value}}},', file=options.output)
            else:
                goodspace = value.rfind(' ', 0, 72 - len(key))
                valuepart = value[:goodspace]
                print(f'    {key} = {{{valuepart}', file=options.output)
                split = value[goodspace:]
                while len(split) >= 76:
                    goodspace = split.rfind(' ', 0, 76)
                    valuepart = split[:goodspace]
                    split = split[goodspace:]
                    print(f'    {valuepart}', file=options.output)
                print(f'    {split}}},', file=options.output)
        print('}', file=options.output)


if __name__ == '__main__':
    main()
