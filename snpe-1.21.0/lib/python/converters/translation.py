#==============================================================================
#
#  Copyright (c) 2018 Qualcomm Technologies, Inc.
#  All Rights Reserved.
#  Confidential and Proprietary - Qualcomm Technologies, Inc.
#
#==============================================================================

class Translation(object):
    def __init__(self):
        self.indexed_methods = {}

    def apply_method(self, method_name, *args):
        return self.indexed_methods[method_name](*args)

    def index_method(self, method_name, method):
        self.indexed_methods[method_name] = method

    def has_indexed_method(self, method_name):
        return method_name in self.indexed_methods

class TranslationBank(object):
    def __init__(self):
        # string type name -> translation
        # the same value may exist for multiple keys.
        self.translations = {}

    def __get_translation(self, op_type):
        if not op_type in self.translations:
            raise KeyError("No translation registered for op type %s" % op_type)
        return self.translations[op_type]

    def apply_specific(self, op_type, method_name, *args):
        translation = self.__get_translation(op_type)
        if not translation.has_indexed_method(method_name):
            raise KeyError("Translation for '%s' does not define an indexed method '%s'" % (op_type, method_name))
        return translation.apply_method(method_name, *args)

    def apply_partial(self, method_name, graph, *args):
        for node in graph.list_nodes():
            translation = self.__get_translation(node.op.type)
            if translation.has_indexed_method(method_name):
                translation.apply_method(method_name, node, graph, *args)

    def apply_total(self, method_name, graph, *args):
        for node in graph.list_nodes():
            self.apply_specific(node.op.type, method_name, node, graph, *args)

    def register(self, translation, *op_types):
        for op_type in op_types:
            if op_type in self.translations:
                raise KeyError("A translation is already registed for op type '%s'" % op_type)
            self.translations[op_type] = translation
