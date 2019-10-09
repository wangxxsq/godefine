#!/usr/bin/env python3

import re
import argparse
import sys
import os


# parse program startup args
def parse_args():
    parser = argparse.ArgumentParser(description="godefine")
    group = parser.add_argument_group()
    #
    group.add_argument('-iv', '--input_vars', type=str, help='use var is specified file')
    group.add_argument('-v', '--vars', type=str, help='use var in command line', nargs='*')
    group.add_argument('-t', '--template', type=str, help='template file', required=True)
    group.add_argument('-o', '--output', type=str, help='output file name')
    #
    group.add_argument('-f', '--force',
                       default=False,
                       action='store_false',
                       help='force generate code,skip any error')
    #
    group.required = False
    args = parser.parse_args()

    print("input_vars file: {}".format(args.input_vars))
    print("vars: {}".format(args.vars))
    print("force: {}".format(args.force))
    print("template file: {}".format(args.template))
    print()
    return args


def parse_tokens(regex_result: dict) -> dict:
    return {
        'var_name': regex_result.get('var_name2') or regex_result.get('var_name'),
        'comment': regex_result.get('comment2') or regex_result.get('comment'),
        'default': regex_result.get('default_val')
    }


# calc align
def get_align(todo_list):
    var_name_align = 0
    comment_align = 0
    for it in todo_list:
        var_name_len = len(it['var_name'])
        # skip ,if name is empty
        if var_name_len == 0:  # todo if not force, just report an error
            continue
        if var_name_len > var_name_align:
            var_name_align = var_name_len

        comment_val_len = len(it['comment'])
        if comment_val_len > comment_align:
            comment_align = comment_val_len
    return var_name_align, comment_align


def grab_vars(input_file: str, var_line: list) -> dict:
    if var_line is None:
        var_line = {}
    out = {}

    if input_file:
        with open(input_file) as var_file:
            for line in var_file.readlines():
                args_line2dict(line, out)
    for it in var_line:
        args_line2dict(it, out)
    return out


def args_line2dict(argv: str, output_dict: dict):
    r = argv.split('=', maxsplit=1)
    if len(r) != 2:
        return
    output_dict[r[0]] = r[1]


def generate_output(input_file: str, output_file: str, var_dict: dict):
    with open(input_file, 'r')as ifile:
        ifile.seek(0, os.SEEK_END)
        flen = ifile.tell()
        ifile.seek(0, os.SEEK_SET)
        ifile_content = ifile.read(flen)

    if ifile_content is None:
        return
    for k, v in var_dict.items():
        ifile_content = re.sub(r'\${%s}' % k, v, ifile_content)
    with open(output_file, 'w') as ofile:
        ofile.write(ifile_content)


def main():
    cmd_args = parse_args()
    user_specified_vars = grab_vars(cmd_args.input_vars, cmd_args.vars)

    regex = re.compile(
        r'''(?P<var_name>((?<={)\w+(?=}))).*(?<=//)\s+(?P<comment>(\b.*))(?=(@default=))\5(?P<default_val>(.*))(?=;)'''
        r'''|((?P<var_name2>((?<={)\w+(?=}))).*(?<=//)\s+(?P<comment2>(\b.*)))''')

    todo_list = []

    with open("consts.go.template") as file:
        for line in file.readlines():
            result = regex.search(line)
            if result:
                result_dict = parse_tokens(result.groupdict())
                todo_list.append(result_dict)

    var_name_align, comment_align = get_align(todo_list)

    vars_no_ready = []

    for it in todo_list:
        var_name = it['var_name']
        default_val = it['default']
        comment = it['comment']
        print('[%s]:\t%-*s' %
              (str(var_name).center(var_name_align + 2), comment_align, comment), end='')
        if default_val:
            print("(default:%s)" % it['default'])
            default_val = it['default']
        else:
            print()
        if default_val is not None and var_name not in user_specified_vars:
            user_specified_vars[var_name] = default_val
        if default_val is None and user_specified_vars.get(var_name) is None:
            vars_no_ready.append(var_name)

    print()
    if len(vars_no_ready) != 0:
        print("error: you must specify manual:", ','.join(vars_no_ready))
        return

    generate_output(cmd_args.template, "output.go", user_specified_vars)
    print("exit...")


if __name__ == '__main__':
    main()
