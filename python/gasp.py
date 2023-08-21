#!/usr/bin/env python3

import argparse
import os
import platform
import re
import sys
import xml.etree.ElementTree as ET
import json
from pathlib import Path


class GaspTypeRefDescription:
    def __init__(self, type_name, type_id):
        self._name = type_name;
        self._id = type_id;
        pass

    def gasp_to_json(self):
        return {
            "name" : self._name,
            "id" : self._id
        };

class GaspAttributeDescription:
    def __init__(self, type_name, member_id, name, brief_description, detailed_description):
        self._type_name = type_name;
        self._id = member_id;
        self._name = name;
        self._brief_description = brief_description;
        self._detailed_description = detailed_description;
        pass

    def gasp_to_json(self):
        return {
            "type" : self._type_name,
            "id" : self._id,
            "name" : self._name,
            "brief_description" : self._brief_description,
            "detailed_description" : self._detailed_description
        };

class GaspFunctionDescription:
    def __init__(self, type_name, member_id, name, brief_description, detailed_description, params):
        self._type_name = type_name;
        self._id = member_id;
        self._name = name;
        self._brief_description = brief_description;
        self._detailed_description = detailed_description;
        self._params = params;
        pass

    def gasp_to_json(self):
        return {
            "type" : self._type_name,
            "id" : self._id,
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
        self._specializations = [];
        self._is_special = False;
        pass

    def append_specialization(self, name, cls_id):
        self._specializations.append({"name" : name, "id" : cls_id});
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
            "public_functions" : self._public_functions,
            "specializations" : self._specializations,
            "is_special" : self._is_special
        };

def strip_class_name_specialization(name): 
    return ''.join(name.partition('<')[0:1]).rstrip();

def is_class_name_specialization(name):
    return strip_class_name_specialization != name;

class GaspEncoder(json.JSONEncoder):
    def default(self, o):
        if "gasp_to_json" in dir(o):
            return o.gasp_to_json();
        return json.JSONEncoder.default(self,o);

def convert_doxy_xml_type_to_type_tuple(type_tag):
    type_tuple = [];
    for ele in type_tag.iter():
        if ele.tag == "type":
            if ele.text:
                type_tuple.append(ele.text.strip());
        elif ele.tag == "ref":
            refid = ele.attrib["refid"];
            refname = ele.text;
            type_tuple.append(GaspTypeRefDescription(
                refname,
                refid
            ));
            if ele.tail:
                type_tuple.append(ele.tail.strip());
    return type_tuple;

def convert_doxy_xml_section_to_attribs(member_section, members_attrib):
    for memberdef in member_section:
        type_name = convert_doxy_xml_type_to_type_tuple(memberdef.find('type'));
        member_id = memberdef.attrib["id"];
        name = memberdef.find('name').text;
        mem_brief_desc = memberdef.find('briefdescription').text;
        mem_detail_desc = [];
        for para in memberdef.find('detaileddescription').findall('para'):
            mem_detail_desc.append(para.text);
        members_attrib.append(GaspAttributeDescription(
            type_name,
            member_id,
            name,
            mem_brief_desc,
            mem_detail_desc
        ));

    pass
def convert_doxy_xml_section_to_functions(member_section, members_func):
    for memberdef in member_section:
        type_name = convert_doxy_xml_type_to_type_tuple(memberdef.find('type'));
        member_id = memberdef.attrib["id"];
        name = memberdef.find('name').text;
        mem_brief_desc = memberdef.find('briefdescription').text;
        mem_detail_desc = [];
        for para in memberdef.find('detaileddescription').findall('para'):
            mem_detail_desc.append(para.text);
        params = [];
        for par in memberdef.findall('param'):
            declname = par.find('declname');
            declname_txt = "";
            if declname is not None:
                declname_txt = declname.text;
            params.append({
                "type" : convert_doxy_xml_type_to_type_tuple(par.find('type')),
                "name" : declname_txt
            });
        members_func.append(GaspFunctionDescription(
            type_name,
            member_id,
            name,
            mem_brief_desc,
            mem_detail_desc,
            params
        ));
    pass

def convert_doxy_xml_to_class(class_tree, xml_text, namespace):
    doxy_root = ET.fromstring(xml_text);

    compound_class = doxy_root.find("compounddef");

    # Find the class id ( used for files/html/etc )
    compound_id = compound_class.attrib['id'];
    # Find the class name 
    compound_name = compound_class.find("compoundname");

    # Find the class descriptions
    class_brief_desc = compound_class.find("briefdescription");
    class_detailed_desc = [];
    for para in compound_class.find('detaileddescription').findall('para'):
        class_detailed_desc.append(para.text);

    # Find the members and sort them properly
    members_priv_func = [];
    members_pub_func = [];

    members_priv_typedef = [];
    members_pub_typedef = [];

    members_priv_var = [];
    members_pub_var = [];

    for section in compound_class.findall('sectiondef'):
        if section.attrib['kind'] == 'private-attrib':
            convert_doxy_xml_section_to_attribs(section.findall('memberdef'), members_priv_var);
        elif section.attrib['kind'] == 'public-attrib':
            convert_doxy_xml_section_to_attribs(section.findall('memberdef'), members_pub_var);
        elif section.attrib['kind'] == 'private-func':
            convert_doxy_xml_section_to_functions(section.findall('memberdef'), members_priv_func);
        elif section.attrib['kind'] == 'public-func':
            convert_doxy_xml_section_to_functions(section.findall('memberdef'), members_pub_func);
    # Strip the namespaced class name with the provided prefix
    class_name = compound_name.text;
    if class_name.startswith(namespace):
        class_name = class_name[len(namespace):]

    # Add the class to the class tree
    gasp_class = GaspClassDescription(
            compound_id,
            class_name,
            class_brief_desc.text,
            class_detailed_desc,
            members_priv_var,
            members_pub_var,
            members_priv_func,
            members_pub_func
    );

    class_tree[compound_id] = gasp_class;

    pass

def main():
    parser = argparse.ArgumentParser(
            prog='gasp',
            description='Converts Doxygen XML to a JSON usable by jinja2 templates'
    );

    parser.add_argument('xml_dir');
    parser.add_argument(
        '-n','--namespace', required=False,
        help='Strips the namespace from the class names',
        default=""
    );

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
                convert_doxy_xml_to_class(class_tree,xml_text,args.namespace);

    for cls_name,cls in class_tree.items():
        stripped_cls_name = strip_class_name_specialization(cls._name);
        if stripped_cls_name != cls._name:
            cls._is_special = True;
            stripped_ids = [];
            for k,v in class_tree.items():
                if v._name == stripped_cls_name:
                    stripped_ids.append(k);
            if len(stripped_ids) != 1:
                print("Panic. This is supposed to be a unique name which exists exactly once. Name: " + stripped_cls_name);
                exit(-1);
            class_tree[stripped_ids[0]].append_specialization(cls_name, class_tree[cls_name]._id);

    print(json.dumps(class_tree,indent=2,cls=GaspEncoder));

    pass

if __name__ == "__main__":
    main();
