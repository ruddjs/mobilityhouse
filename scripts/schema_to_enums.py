#!/usr/bin/env python
import sys
import re
import json
from pathlib import Path


def create_class(name):
    return normalclass(name)


def create_attribute(name):
    # Assumes the variable name is a concatenation of capitalized therms, e.g.,
    # "CamelCase" or "SuperHyperMega"
    # Convert to CamelCase
    name_camel_case = name[0].lower() + name[1:]

    return attribute(name, name_camel_case)


class normalclass:
    def __init__(self, name):
        self.name = name
        self.attrs = []

    def add_attr(self, attr):
        self.attrs.append(attr)

    def __str__(self):
        output = f"class {self.name}:\n"

        if len(self.attrs) == 0:
            return output + "    pass\n"

        for attr in self.attrs:
            output += str(attr)

        return output


class attribute:
    def __init__(self, name, name_camel_case):
        self.name = name
        self.name_camel_case = name_camel_case

    def __str__(self):
        name = self.name
        name_camel_case = self.name_camel_case
        if not re.match("^[a-zA-Z_]", self.name):
            name = "_" + self.name

        definition = f'    {name_camel_case} = "{name}"\n'

        return definition

    def __repr__(self):
        return f"<{self.name}, {self.name_camel_case}> "



enum_types = []
enum_types_names = []


def parse_schema(schema):
    with open(schema, "r") as f:
        schema = json.loads(f.read())

    try:
        definitions = schema['definitions']
    except KeyError:
       pass

    for enum_type, value in definitions.items():
        if "Enum" in enum_type:
            type_name = enum_type.replace("Enum", '')
            if type_name not in enum_types_names:
                nc = create_class(type_name)
                for enum_attr in value['enum']:
                    attr = create_attribute(enum_attr)
                    nc.add_attr(attr)
                enum_types.append(nc)
                enum_types_names.append(nc.name)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Pass path to folder with schemas")
        sys.exit(-1)

    p = Path(sys.argv[1])
    schemas = list(p.glob("*.json"))

    for schema in schemas:
        parse_schema(schema)

    with open('enums.py', 'wb+') as f:
        for enum_type in sorted(enum_types, key=lambda enum_type: enum_type.name):
            f.write(b"\n\n")
            f.write(str(enum_type).encode('utf-8'))
