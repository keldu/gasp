#!/usr/bin/env python3

import argparse
import os
import platform
import re
import sys
import xml.etree.ElementTree as ET
import json
from pathlib import Path

class GaspAttributeDescription:
    def __init__(self, type_name, name, brief_description, detailed_description):
        self._type_name = type_name;
        self._name = name;
        self._brief_description = brief_description;
        self._detailed_description = detailed_description;
        pass

    def gasp_to_json(self):
        return {
            "type" : self._type_name,
            "name" : self._name,
            "brief_description" : self._brief_description,
            "detailed_description" : self._detailed_description
        };

class GaspFunctionDescription:
    def __init__(self, type_name, name, brief_description, detailed_description, params):
        self._type_name = type_name;
        self._name = name;
        self._brief_description = brief_description;
        self._detailed_description = detailed_description;
        self._params = params;
        pass

    def gasp_to_json(self):
        return {
            "type" : self._type_name,
            "name" : self._name,
            "brief_description" : self._brief_description,
            "detailed_description" : self._detailed_description,
            "parameters" : self._params
        };

class GaspClassDescription:
    def __init__(self, class_id, name, brief_description, detailed_description,
                 private_attributes, public_attributes,
                 private_functions, public_functions
    ):
        self._id = class_id;
        self._name = name;
        self._brief_description = brief_description;
        self._detailed_description = detailed_description;

        self._private_attributes = private_attributes;
        self._public_attributes = public_attributes;
        
        self._private_functions = private_functions;
        self._public_functions = public_functions;
        pass
        
    def gasp_to_json(self):
        return {
            "id" : self._id,
            "name" : self._name,
            "brief_description" : self._brief_description,
            "detailed_description" : self._detailed_description,
            "private_attributes" : self._private_attributes,
            "public_attributes" : self._public_attributes,
            "private_functions" : self._private_functions,
            "public_functions" : self._public_functions
        };

class GaspEncoder(json.JSONEncoder):
    def default(self, o):
        if "gasp_to_json" in dir(o):
            return o.gasp_to_json();
        return json.JSONEncoder.default(self,o);

def convert_doxy_xml_to_class(class_tree, xml_text):
    doxy_root = ET.fromstring(xml_text);

    compound_class = doxy_root.find("compounddef");

    # Find the class id ( used for files/html/etc )
    compound_id = compound_class.attrib['id'];
    # Find the class name 
    compound_name = compound_class.find("compoundname");

    # Find the class descriptions
    class_brief_desc = compound_class.find("briefdescription");
    class_detailed_desc = compound_class.find("detaileddescription");

    # Find the members and sort them properly
    members_priv_func = [];
    members_pub_func = [];

    members_priv_typedef = [];
    members_pub_typedef = [];

    members_priv_var = [];
    members_pub_var = [];

    for section in compound_class.findall('sectiondef'):
        if section.attrib['kind'] == 'private-attrib':
            for memberdef in section.findall('memberdef'):
                type_name = memberdef.find('type').text;
                name = memberdef.find('name').text;
                mem_brief_desc = memberdef.find('briefdescription').text;
                mem_detail_desc = memberdef.find('detaileddescription').text;
                members_priv_var.append(GaspAttributeDescription(
                    type_name,
                    name,
                    mem_brief_desc,
                    mem_detail_desc
                ));
        elif section.attrib['kind'] == 'public-attrib':
            for memberdef in section.findall('memberdef'):
                type_name = memberdef.find('type').text;
                name = memberdef.find('name').text;
                mem_brief_desc = memberdef.find('briefdescription').text;
                mem_detail_desc = memberdef.find('detaileddescription').text;
                members_pub_var.append(GaspAttributeDescription(
                    type_name,
                    name,
                    mem_brief_desc,
                    mem_detail_desc
                ));
        elif section.attrib['kind'] == 'private-func':
            for memberdef in section.findall('memberdef'):
                type_name = memberdef.find('type').text;
                name = memberdef.find('name').text;
                mem_brief_desc = memberdef.find('briefdescription').text;
                mem_detail_desc = memberdef.find('detaileddescription').text;
                params = [];
                for par in memberdef.findall('param'):
                    declname = par.find('declname');
                    declname_txt = "";
                    if declname is not None:
                        declname_txt = declname.text;
                    params.append({
                        "type" : par.find('type').text,
                        "name" : declname_txt
                    });
                members_priv_func.append(GaspFunctionDescription(
                    type_name,
                    name,
                    mem_brief_desc,
                    mem_detail_desc,
                    params
                ));
        elif section.attrib['kind'] == 'public-func':
            for memberdef in section.findall('memberdef'):
                type_name = memberdef.find('type').text;
                name = memberdef.find('name').text;
                mem_brief_desc = memberdef.find('briefdescription').text;
                mem_detail_desc = memberdef.find('detaileddescription').text;
                params = [];
                for par in memberdef.findall('param'):
                    declname = par.find('declname');
                    declname_txt = "";
                    if declname is not None:
                        declname_txt = declname.text;
                    params.append({
                        "type" : par.find('type').text,
                        "name" : declname_txt
                    });
                members_pub_func.append(GaspFunctionDescription(
                    type_name,
                    name,
                    mem_brief_desc,
                    mem_detail_desc,
                    params
                ));
    # 
    gasp_class = GaspClassDescription(
            compound_id,
            compound_name.text,
            class_brief_desc.text,
            class_detailed_desc.text,
            members_priv_var,
            members_pub_var,
            members_priv_func,
            members_pub_func
    );

    class_tree[compound_name.text] = gasp_class;

    pass

def main():
    parser = argparse.ArgumentParser(
            prog='gasp',
            description='Converts Doxygen XML to a JSON usable by jinja2 templates'
    );

    parser.add_argument('xml_dir');

    args = parser.parse_args();

    xml_dir = Path(args.xml_dir);
    if xml_dir.is_file():
        print("XML dir path is not a dir");
        exit(-1);

    class_tree = {};
    for p in xml_dir.iterdir():
        if p.name.startswith('class'):
            if p.is_file():
                xml_file = open(p, "r");
                xml_text = xml_file.read();
                convert_doxy_xml_to_class(class_tree,xml_text);


    print(json.dumps(class_tree,indent=2,cls=GaspEncoder));

    pass

if __name__ == "__main__":
    main();
