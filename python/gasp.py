#!/usr/bin/env python3

import argparse
import os
import platform
import re
import sys
import xml.etree.ElementTree as ET
import json
from pathlib import Path


class GaspFileDescription:
    def __init__(self, f_id, f_name, attribs, funcs):
        self._id = f_id;
        self._name = f_name;
        self._attributes = attribs;
        self._functions = funcs;
        pass

    def gasp_to_json(self):
        return {
            "id" : self._id,
            "name" : self._name,
            "functions" : self._functions,
            "attributes" : self._attributes
        };

class GaspNamespaceDescription:
    def __init__(self, ns_id, ns_name, attribs, funcs):
        self._id = ns_id;
        self._name = ns_name;
        self._attributes = attribs;
        self._functions = funcs;
        pass

    def gasp_to_json(self):
        return {
            "id" : self._id,
            "name" : self._name,
            "functions" : self._functions,
            "attributes" : self._attributes
        };

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
    def __init__(self, member_id, name):
        self._type_name = [];
        self._id = member_id;
        self._name = name;
        self._brief_description = "";
        self._detailed_description = [];
        self._static = False;
        pass

    def gasp_to_json(self):
        return {
            "type" : self._type_name,
            "id" : self._id,
            "name" : self._name,
            "brief_description" : self._brief_description,
            "detailed_description" : self._detailed_description,
            "static" : self._static
        };

class GaspFunctionDescription:
    def __init__(self, member_id, name):
        self._type_name = [];
        self._id = member_id;
        self._name = name;
        self._brief_description = "";
        self._detailed_description = [];
        self._params = [];
        self._static = False;
        pass

    def gasp_to_json(self):
        return {
            "type" : self._type_name,
            "id" : self._id,
            "name" : self._name,
            "brief_description" : self._brief_description,
            "detailed_description" : self._detailed_description,
            "parameters" : self._params,
            "static" : self._static
        };

class GaspClassDescription:
    def __init__(self, class_id, name,
                 attributes,
                 functions
    ):
        self._id = class_id;
        self._name = name;
        self._brief_description = "";
        self._detailed_description = [];

        self._attributes = attributes;
        self._functions = functions;

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
            "attributes" : self._attributes,
            "functions" : self._functions,
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
        #endfor

        members_attrib[member_id]._type_name = type_name;
        members_attrib[member_id]._brief_description = mem_brief_desc;
        members_attrib[member_id]._detailed_description = mem_detail_desc;
        member_static = False;
        if memberdef.attrib['static'] == "yes":
            member_static = True;
        #endif
        members_attrib[member_id]._static = member_static;
    #endfor

    pass
def convert_doxy_xml_section_to_functions(member_section, members_func):
    for memberdef in member_section:
        type_name = convert_doxy_xml_type_to_type_tuple(memberdef.find('type'));
        member_id = memberdef.attrib["id"];

        mem_brief_desc = memberdef.find('briefdescription').text;
        mem_detail_desc = [];
        for para in memberdef.find('detaileddescription').findall('para'):
            mem_detail_desc.append(para.text);
        #endfor
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
        #endfor

        members_func[member_id]._type_name = type_name;
        members_func[member_id]._brief_description = mem_brief_desc;
        members_func[member_id]._detailed_description = mem_detail_desc;
        members_func[member_id]._params = params;
        member_static = False;
        if memberdef.attrib['static'] == "yes":
            member_static = True;
        #endif
        members_func[member_id]._static = member_static;
    #endfor
    pass

def convert_doxy_xml_to_class(class_tree, xml_text, namespace):
    doxy_root = ET.fromstring(xml_text);

    compound_class = doxy_root.find("compounddef");

    # Find the class id ( used for files/html/etc )
    compound_id = compound_class.attrib['id'];

    # Find the class descriptions
    class_brief_desc = compound_class.find("briefdescription");
    class_tree._brief_description = class_brief_desc.text;
    for para in compound_class.find('detaileddescription').findall('para'):
        class_tree._detailed_description.append(para.text);

    for section in compound_class.findall('sectiondef'):
        section_kind = section.attrib['kind'];
        if section_kind == 'private-attrib' or section_kind == 'public-static-attrib' or section_kind == 'public-attrib' or section_kind == 'private-static-attrib':
            convert_doxy_xml_section_to_attribs(section.findall('memberdef'), class_tree._attributes);
        elif section.attrib['kind'] == 'private-func':
            convert_doxy_xml_section_to_functions(section.findall('memberdef'), class_tree._functions);
        elif section.attrib['kind'] == 'public-func':
            convert_doxy_xml_section_to_functions(section.findall('memberdef'), class_tree._functions);

    pass

def convert_doxy_index_xml_to_index(xml_text, doxy_tree, namespace):
    doxy_index_root = ET.fromstring(xml_text);
    for compound in doxy_index_root.findall('compound'):
        compound_kind = compound.attrib['kind'];
        compound_id = compound.attrib['refid'];
        compound_name = compound.find('name').text;
        if compound_kind == 'class' or compound_kind == 'struct':
            attribs = {};
            funcs = {};

            for member in compound.findall('member'):
                member_kind = member.attrib['kind'];
                member_id = member.attrib['refid'];
                member_name = member.find('name').text;
                if member_kind == 'function':
                    gasp_func = GaspFunctionDescription(
                        member_id,
                        member_name
                    );
                    funcs[member_id] = gasp_func;
                elif member_kind == 'variable':
                    gasp_attrib = GaspAttributeDescription(
                        member_id,
                        member_name
                    );
                    attribs[member_id] = gasp_attrib;
                #endif
            #endfor
            # Strip the namespaced class name with the provided prefix
            class_name = compound_name;
            if class_name.startswith(namespace):
                class_name = class_name[len(namespace):]
            #endif

            gasp_class = GaspClassDescription(
                compound_id,
                class_name,
                attribs,
                funcs
            );
            doxy_tree['classes'][compound_id] = gasp_class;
        elif compound_kind == 'namespace':
            attribs = {};
            funcs = {};

            for member in compound.findall('member'):
                member_kind = member.attrib['kind'];
                member_id = member.attrib['refid'];
                member_name = member.find('name').text;

                if member_kind == 'function':
                    gasp_func = GaspFunctionDescription(
                        member_id,
                        member_name
                    );
                    funcs[member_id] = gasp_func;
                elif member_kind == 'variable':
                    gasp_attrib = GaspAttributeDescription(
                        member_id,
                        member_name
                    );
                    attribs[member_id] = gasp_attrib;
                #endif
            #endfor
            gasp_namespace = GaspNamespaceDescription(
                compound_id,
                compound_name,
                attribs,
                funcs
            );
            doxy_tree['namespaces'][compound_id] = gasp_namespace;
        elif compound_kind == 'file':
            attribs = {};
            funcs = {};

            for member in compound.findall('member'):
                member_kind = member.attrib['kind'];
                member_id = member.attrib['refid'];
                member_name = member.find('name').text;

                if member_kind == 'function':
                    gasp_func = GaspFunctionDescription(
                        member_id,
                        member_name
                    );
                    funcs[member_id] = gasp_func;
                elif member_kind == 'variable':
                    gasp_attrib = GaspAttributeDescription(
                        member_id,
                        member_name
                    );
                    attribs[member_id] = gasp_attrib;
                #endif
            #endfor
            gasp_file = GaspFileDescription(
                compound_id,
                compound_name,
                attribs,
                funcs
            );
            doxy_tree['files']['compound_id'] = gasp_file;
        #endif
    #endfor
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

    namespace = args.namespace + "::";

    xml_dir = Path(args.xml_dir);
    if xml_dir.is_file():
        print("XML dir path is not a dir");
        exit(-1);
    #endif

    doxy_tree = {
        "classes" : {},
        "namespaces" : {},
        "files" : {}
    };

    index_path = xml_dir/"index.xml";
    if index_path.is_file():
        index_xml_file = open(index_path, "r");
        xml_index_text = index_xml_file.read();
        convert_doxy_index_xml_to_index(xml_index_text, doxy_tree, namespace);
    else:
        print("XML Index file doesn't exist");
        exit(-1);
    #endif
    
    for cls_key,cls in doxy_tree['classes'].items():
        cls_file_name = cls._id + ".xml";
        p = xml_dir/cls_file_name;
        if p.is_file():
            cls_xml_file = open(p, "r");
            cls_xml_text = cls_xml_file.read();
            convert_doxy_xml_to_class(cls,cls_xml_text,namespace);
        else:
            print("Class file is missing");
            exit(-1);
        #endif
    #endfor

    for key,cls in doxy_tree["classes"].items():
        stripped_cls_name = strip_class_name_specialization(cls._name);
        if stripped_cls_name != cls._name:
            cls._is_special = True;
            stripped_ids = [];
            for k,v in doxy_tree["classes"].items():
                if v._name == stripped_cls_name:
                    stripped_ids.append(k);
                #endif
            #endfor
            if len(stripped_ids) != 1:
                print("Panic. This is supposed to be a unique name which exists exactly once. Name: " + stripped_cls_name + "\nMatching IDs: " + json.dumps(stripped_ids, indent=2));
                exit(-1);
            #endif
            doxy_tree["classes"][stripped_ids[0]].append_specialization(cls._name, key);
        #endif
    #endfor

    print(json.dumps(doxy_tree,indent=2,cls=GaspEncoder));
    pass

if __name__ == "__main__":
    main();
#endif
