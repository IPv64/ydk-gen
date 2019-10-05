#  ----------------------------------------------------------------
# Copyright 2016 Cisco Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------
""" _encoder.py

   Encoder.

"""
import logging

from ._validator import validate_entity, is_yvalidate
from ._value_encoder import ValueEncoder
from lxml import etree
from ydk._core._dm_meta_info import REFERENCE_CLASS, REFERENCE_LIST , REFERENCE_LEAFLIST, \
                                 REFERENCE_UNION, ANYXML_CLASS, REFERENCE_BITS, \
                                 REFERENCE_IDENTITY_CLASS, REFERENCE_ENUM_CLASS
from ydk.types import Empty, DELETE, REMOVE, MERGE, REPLACE, CREATE, READ, Decimal64, YList, YLeafList, YListItem
from ydk.errors import YPYModelError

from ._importer import _yang_ns


class XmlEncoder(object):
    def __init__(self):
        self.encode_value = ValueEncoder().encode

    def encode(self, entity):
        ''' Convert the entity to an xml payload '''
        return etree.tostring(self.encode_to_xml(entity, etree.Element('a'), '', validate=is_yvalidate(entity)),
                              method='xml', pretty_print='True', encoding='utf-8').decode('utf-8')

    def encode_to_xml(self, entity, root, optype, is_filter=False, validate=True):
        ''' Convert the entity to an xml payload '''
        # if the entity has a parent hierarchy use that to get
        # the parent related envelope that we need
        if not has_yfilter(entity) and ((hasattr(entity, 'mtype') and not entity.mtype == ANYXML_CLASS) and
                                        (not is_filter and hasattr(entity, '_has_data') and not entity._has_data())):
            return

        if validate:
            validate_entity(entity, optype)

        if entity_is_rpc_input(entity):
            elem = root
        else:
            elem = etree.SubElement(root, entity.i_meta.yang_name)
            if hasattr(entity, 'yfilter'):
                yfilter = getattr(entity, 'yfilter')
                if is_edit_yfilter(yfilter):
                    xc = 'urn:ietf:params:xml:ns:netconf:base:1.0'
                    elem.set('{' + xc + '}operation', get_yfilter_tag(yfilter))
            parent_ns = None
            current_parent = root
            while current_parent is not None and parent_ns is None:
                parent_ns = current_parent.get('xmlns')
                current_parent = current_parent.getparent()

            if entity.i_meta.namespace is not None and parent_ns != entity.i_meta.namespace:
                elem.set('xmlns', entity.i_meta.namespace)

        for member in entity.i_meta.meta_info_class_members:
            value = getattr(entity, member.presentation_name)
            if value is None or isinstance(value, list) and value == [] and not has_yfilter(value):
                continue

            if not has_yfilter(value) and (not member.mtype == ANYXML_CLASS and hasattr(value, '_has_data') and not value._has_data()):
                continue

            member_elem = None
            NSMAP = {}
            if member.mtype not in [REFERENCE_CLASS, REFERENCE_LIST, REFERENCE_LEAFLIST, REFERENCE_IDENTITY_CLASS,
                                    REFERENCE_UNION] or is_edit_yfilter(value) or isinstance(value, READ):
                if entity.i_meta.namespace is not None \
                   and entity.i_meta.namespace != _yang_ns._namespaces[member.module_name]:
                    NSMAP[None] = _yang_ns._namespaces[member.module_name]
                member_elem = etree.SubElement(elem, member.name, nsmap=NSMAP)
                if member.mtype == ANYXML_CLASS:
                    self.encode_to_xml(value, member_elem, optype, validate=is_yvalidate(value, validate))
                    continue

            if is_edit_yfilter(value) and not is_filter:
                xc = 'urn:ietf:params:xml:ns:netconf:base:1.0'
                member_elem.set('{' + xc + '}operation', get_yfilter_tag(value))
                if is_value_edit_yfilter(value):
                    if member.mtype == REFERENCE_UNION:
                        union_list = member.get_all_union_members()
                        for union_member in union_list:
                            try:
                                member_elem.text = self.encode_value(union_member, NSMAP, value.value(), validate)
                                if member_elem.text:
                                    break
                            except YPYModelError:
                                continue
                        if not member_elem.text and validate:
                            ydk_logger = logging.getLogger(__name__)
                            error_msg = "Could not encode leaf '{0}', to union types: {1}, value: {2}".\
                                format(member.name, [m.ptype for m in union_list], value)
                            ydk_logger.error(error_msg)
                            raise YPYModelError(error_msg)
                    else:
                        member_elem.text = self.encode_value(member, NSMAP, value.value(), validate)
            elif isinstance(value, READ):
                continue
            elif member.mtype == REFERENCE_CLASS:
                self.encode_to_xml(value, elem, optype, validate=is_yvalidate(value, validate))
            elif member.mtype == REFERENCE_LIST:
                child_list = value
                for child in child_list:
                    self.encode_to_xml(child, elem, optype, validate=is_yvalidate(child, validate))
            elif member.mtype == REFERENCE_LEAFLIST and isinstance(value, list):
                if hasattr(value, 'yfilter'):
                    yfilter = getattr(value, 'yfilter')
                    if is_edit_yfilter(yfilter):
                        member_elem = etree.SubElement(elem, member.name, nsmap=NSMAP)
                        xc = 'urn:ietf:params:xml:ns:netconf:base:1.0'
                        member_elem.set('{' + xc + '}operation', get_yfilter_tag(yfilter))
                        continue

                for child in value:
                    if entity.i_meta.namespace is not None and entity.i_meta.namespace != _yang_ns._namespaces[member.module_name]:
                        NSMAP[None] = _yang_ns._namespaces[member.module_name]
                    text = self.encode_value(member, NSMAP, child.item, validate)
                    member_elem = etree.SubElement(elem, member.name, nsmap=NSMAP)
                    member_elem.text = text
                    if hasattr(child, 'yfilter'):
                        xc = 'urn:ietf:params:xml:ns:netconf:base:1.0'
                        yfilter = getattr(child, 'yfilter')
                        member_elem.set('{' + xc + '}operation', get_yfilter_tag(yfilter))

            elif member.mtype == REFERENCE_UNION and isinstance(value, list):
                for leaf in value:
                    self._encode_union_member(entity, member, leaf, elem, {}, validate)

            elif member.mtype == REFERENCE_UNION:
                self._encode_union_member(entity, member, value, elem, {}, validate)

            elif member.mtype == REFERENCE_IDENTITY_CLASS:
                text = self.encode_value(member, NSMAP, value, validate)
                member_elem = etree.SubElement(elem, member.name, nsmap=NSMAP)
                member_elem.text = text
            else:
                member_elem.text = self.encode_value(member, NSMAP, value, validate)
        return elem

    def encode_filter(self, filter, root, optype):
        self.encode_to_xml(filter, root, optype, True, is_yvalidate(filter))

    def _encode_union_member(self, entity, contained_member, value, elem, NSMAP, validate):
        member_elem = None
        if contained_member.mtype == REFERENCE_UNION:
            for sub_member in contained_member.members:
                if self._encode_union_member(entity, sub_member, value, elem, NSMAP, validate):
                    return True
            return False    # error conditions
        elif contained_member.mtype == REFERENCE_LEAFLIST:
            if isinstance(value, YListItem):
                value = value.item
            t = self.encode_value(contained_member, NSMAP, value, is_yvalidate(entity, validate), silent=True)
            if len(t) > 0:
                member_elem = etree.SubElement(elem, contained_member.name, nsmap=NSMAP)
                if entity.i_meta.namespace is not None and entity.i_meta.namespace != _yang_ns._namespaces[contained_member.module_name]:
                    NSMAP[None] = _yang_ns._namespaces[contained_member.module_name]
                member_elem.text = t
                return True
            else:
                return False
        else:
            t = self.encode_value(contained_member, NSMAP, value, is_yvalidate(entity, validate), silent=True)
            if len(t) == 0:
                return False
            member_elem = etree.SubElement(elem, contained_member.name, nsmap=NSMAP)
            member_elem.text = t
            if len(member_elem.text) > 0:
                return True
        return False


def entity_is_rpc_input(entity):
    return hasattr(entity, 'parent') and \
        entity.parent is not None and \
        hasattr(entity.parent, 'is_rpc') and \
        entity.parent.is_rpc and \
        entity._meta_info().yang_name == 'input'


def has_yfilter(entity):
    if entity is None:
        return False
    if hasattr(entity, 'yfilter') and entity.yfilter:
        return True
    if not hasattr(entity, 'i_meta'):
        return False
    for member in entity.i_meta.meta_info_class_members:
        value = getattr(entity, member.presentation_name)
        if member.mtype == REFERENCE_CLASS:
            if has_yfilter(value):
                return True
        elif member.mtype == REFERENCE_LIST:
            try:
                for v in value:
                    if has_yfilter(v):
                        return True
            except TypeError:
                continue
        elif member.mtype == REFERENCE_LEAFLIST:
            if has_yfilter(value):
                return True
    return False


def is_edit_yfilter(yfilter):
    return isinstance(yfilter, DELETE) or isinstance(yfilter, REMOVE) or isinstance(yfilter, MERGE) or \
           isinstance(yfilter, REPLACE) or isinstance(yfilter, CREATE)


def is_value_edit_yfilter(yfilter):
    return (isinstance(yfilter, MERGE) or isinstance(yfilter, REPLACE) or isinstance(yfilter, CREATE)) and\
           yfilter.value() is not None


def get_yfilter_tag(yfilter):
    tag = ''
    if isinstance(yfilter, DELETE):
        tag = 'delete'
    elif isinstance(yfilter, REMOVE):
        tag = 'remove'
    elif isinstance(yfilter, MERGE):
        tag = 'merge'
    elif isinstance(yfilter, REPLACE):
        tag = 'replace'
    elif isinstance(yfilter, CREATE):
        tag = 'create'
    return tag
