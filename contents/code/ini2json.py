# -*- coding: utf-8 -*-
import json
import sys
import pyperclip as pc
from collections.abc import MutableMapping
from configparser import (ConfigParser, MissingSectionHeaderError,
                          ParsingError, DEFAULTSECT)


class StrictConfigParser(ConfigParser):

    def _read(self, fp, fpname):
        cursect = None                        # None, or a dictionary
        optname = None
        lineno = 0
        e = None                              # None, or an exception
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
            # continuation line?
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname].append(value)
            # a section header or option header?
            else:
                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        raise ValueError('Duplicate section %r' % sectname)
                    elif sectname == DEFAULTSECT:
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    try:
                        mo = self._optcre.match(line)   # 2.7
                    except AttributeError:
                        mo = self.OPTCRE.match(line)    # 2.6
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        optname = self.optionxform(optname.rstrip())
                        # This check is fine because the OPTCRE cannot
                        # match if it would set optval to None
                        if optval is not None:
                            if vi in ('=', ':') and ';' in optval:
                                # ';' is a comment delimiter only if it follows
                                # a spacing character
                                pos = optval.find(';')
                                if pos != -1 and optval[pos - 1].isspace():
                                    optval = optval[:pos]
                            optval = optval.strip()
                            # allow empty values
                            if optval == '""':
                                optval = ''
                            cursect[optname] = [optval]
                        else:
                            # valueless option handling
                            cursect[optname] = optval
                    else:
                        # a non-fatal parsing error occurred.  set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

        # join the multi-line values collected while reading
        all_sections = [self._defaults]
        all_sections.extend(self._sections.values())
        for options in all_sections:
            for name, val in options.items():
                if isinstance(val, list):
                    options[name] = '\n'.join(val)

    def dget(self, section, option, default=None, type=str):
        if not self.has_option(section, option):
            return default
        if type is str:
            return self.get(section, option)
        elif type is int:
            return self.getint(section, option)
        elif type is bool:
            return self.getboolean(section, option)
        else:
            raise NotImplementedError()



def getSection(praser, section):
    area = {}
    for name, value in praser.items(section):
        area[name] = value
        if len(area[name]) == 1:
            area[name] = str(area[name][0])
        elif len(area[name]) == 0:
            area[name] = ''
    return area

def flatten(dictionary, parent_key='', separator=']['):
    items = {}

    for key, value in dictionary.items():
        new_key = parent_key + separator + str(key) if parent_key else key
        if isinstance(value, MutableMapping):
            items.update(flatten(value, new_key, separator=separator))
        else:
            if parent_key not in items:
                items[parent_key] = {}
            items[parent_key][key] = value

    return items

def write(data, filepath):
    out = flatten(data)

    config = ConfigParser()
    config.optionxform = str

    for section in out:
        config.add_section(section)
        for key in out[section]:
            config.set(section, key, out[section][key])

    #with open('ini2json.ini', 'w') as configfile:
    with open(filepath, 'a+') as configfile:
        config.write(configfile)

    #result = json.dumps(out, indent=4)

    #f = open("ini2json.json", "w")
    #f.write(result)
    #f.close()

def read(filepath):
    praser = ConfigParser(delimiters=('='), strict=False)
    praser.optionxform = str
    f = open(filepath)
    praser.readfp(f)
    f.close()

    json_data = {}

    for item in praser.sections():
        j = json_data
        parts = item.split('][')
        for index in range(len(parts)):
            part = parts[index]
            if (index + 1 == len(parts)):
                j = j.setdefault(part, getSection(praser, item))
            else:
                j = j.setdefault(part, {})

    return json_data

    #result = json.dumps(json_data, indent=4)

    #f = open("ini2json.json", "w")
    #f.write(result)
    #f.close()
    
    #print(result)