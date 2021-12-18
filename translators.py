#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import polib
import sys
import os
import fnmatch
from findfiles import FindFiles
import re

def get_translators_from_comments(filename):
    translators = []
    cnt = 0
    try:
        with open(filename) as f:
            while True:
                line = f.readline()

                if not line:
                    break

                cnt += 1
                if cnt > 20:
                    break

                # Example: Jordi Mas <jmas@softcatala.org>, 2021
                result = re.search('\#(.*)(<.*>).*?', line)
                if not result:
                    continue

                name = result.group(1)
                if len(name.strip()) < 2:
                    continue

                if 'FIRST' in name or 'xml:lang' in name:
                    continue

                if 'NSBox' in name:
                    continue

                translator = clean_translator_name(name)
                translators.append(name.strip())

    except Exception as e:
        print(f"error: {filename} - {e}")

    return translators

def clean_translator_name(translator):
    pos = translator.find("<")
    if pos >= 0:
        old = translator
        translator = translator[:pos-1]
#        print(f"Clean {old}->{translator}")                            

    pos = translator.find("http")
    if pos >= 0:
        old = translator 
        translator = translator[:pos-1]
#        print(f"Clean {old}->{translator}")

    pos = translator.find(", 2")
    if pos >= 0:
        old = translator 
        translator = translator[:pos-1]
#        print(f"Clean {old}->{translator}")

    return translator

def get_translators_from_credits(filename):

    translators = []

    try:
        source_po = polib.pofile(filename)
        for entry in source_po:
            id = entry.msgid
            msg = entry.msgstr

            if 'translator-credits' not in id:
                continue

            pos = msg.find("<")
            if pos >= 0:
                msg = msg[:pos-1]

            if len(msg.strip()) < 2:
                continue

            if '\n' in msg:
               splitted_translators = msg.split("\n")
               for translator in splitted_translators:
                    translator = translator.strip()
                    if len(translator) < 2:
                        continue

                    translator = clean_translator_name(translator)                   
#                    print(f"Split: '{translator}'")
                    translators.append(translator)
            else:
                translator = msg.strip()
                translator = clean_translator_name(translator)
                translators.append(translator)

    except Exception as e:
        print(f"error: {filename} - {e}")

    return translators

def clean_up(translators):

    filtered = set()
    last_translator = ""
    for translator in translators:
        components = translator.split(" ")
        last_components = last_translator.split(" ")

        if len(components) > 1 and len(last_components) > 1:
            current = f"{components[0]} {components[1]}".lower()
            last = f"{last_components[0]} {last_components[1]}".lower()
 #           print(f"{current} - {last}")

            if last == current:
#                print(last)
#                print(current)
                print(f"Not adding '{translator}' because of '{last_translator}'")
                continue

        translator = translator[0].upper() + translator[1:]
        filtered.add(translator)
        last_translator = translator                        

    return sorted(filtered)

def main():

    print("Extract translator names")

    changes = 0
    directory = '/home/jordi/sc/tmt/tmt/src/output/individual_pos/'
    files = FindFiles().find_recursive(directory, "*.po")

    translators = set()
    cnt = 0
    for file in files:
#        if cnt > 5000:
#            break

        translators_comments = get_translators_from_comments(file)

        for translator in translators_comments:
            #print(translator)
            translators.add(translator)

        translators_credits = get_translators_from_credits(file)

        for translator in translators_credits:
            #print(translator)
            translators.add(translator)

        cnt += 1

    translators = clean_up(sorted(translators))

    saved = 0
    with open("translators.txt", "w") as f:
        for translator in translators:
            if len(translator.split()) < 2:
#                print(f"Discard {translator}")
                continue

            saved += 1
            f.write(f"{translator}\n")
#            print(translator)

    print(f"files: {len(files)}")
    print(f"translators: {saved}")
    return

if __name__ == "__main__":
    main()
