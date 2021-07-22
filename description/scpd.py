from xml.etree.ElementTree import Element

from description import XmlParser
from description import *

class StateVar(XmlParser):
    def __init__(self, child: Element) -> None:
        super().__init__(child=child)

        self.attr = dict()
        if child.attrib:
            self.attr = child.attrib

    def parse_item(self, item: Element):
        name = getname(item.tag)

        if name in [NODE_NAME, NODE_DEFAULT_VALUE, NODE_DATA_TYPE]:
            self.setdefault(name, item.text)
        elif name == NODE_ALLOWED_LIST:
            allowed = [child.text for child in item.getchildren()]
            self.setdefault(name, allowed)
        elif name == NODE_ALLOWED_RANGE:
            range_ = {getname(child.tag): child.text for child in item.getchildren()}
            self.setdefault(name, range_)

class Argument(XmlParser):
    def __init__(self, child: Element) -> None:
        super().__init__(child=child)

    def parse_item(self, item: Element):
        name = getname(item.tag)

        self.setdefault(name, item.text)

class Action(XmlParser):
    def __init__(self, child: Element) -> None:
        super().__init__(child=child)

    def parse_item(self, item: Element):
        name = getname(item.tag)

        if name == NODE_NAME:
            self.setdefault(name, item.text)
        elif name == NODE_ARGUMENT_LIST:
            arguments = []
            for argument in item.getchildren():
                arguments.append(Argument(argument))
            self.setdefault(name, arguments)

class scpd(dict):
    def __init__(self, child: Element) -> None:
        super().__init__()

        if child:
            for item in child.getchildren():
                if item:
                    self.parse_item(item=item)

    def parse_item(self, item: Element):
        name = getname(item.tag)

        if name == NODE_SPEC_VERSION:
            self.setdefault(name, [item[0].text, item[1].text])
        elif name == NODE_ACTION_LIST:
            actions = [Action(a) for a in item.getchildren()]
            self.setdefault(name, actions)
        elif name == NODE_STATE_TABLE:
            statevars = [StateVar(s) for s in item.getchildren()]
            self.setdefault(name, statevars)

    def print_actions(self):
        print("\n[>] scpd - Printing all related actions:")
        for action in self[NODE_ACTION_LIST]:
            print("    | %s" % (action[NODE_NAME]))
            for arg in action[NODE_ARGUMENT_LIST]:
                print(
                    " " * 8
                    + "| %s: direction=%s (relatedVar=%s)"
                    % (
                        arg[NODE_NAME],
                        arg[NODE_DIRECTION],
                        arg.get(NODE_RELATED_VARIABLE),
                    )
                )
        print()

    def print_state_table(self):
        print("\n[>] scpd - Printing all related state-variables:")
        for var in self[NODE_STATE_TABLE]:
            print("    | %s: %s" % (var[NODE_NAME], var[NODE_DATA_TYPE]))

            for key in [NODE_DEFAULT_VALUE, NODE_DEFAULT_TYPE]:
                print(" " * 8 + "| %s: %s" % (key, var.get(key)))

            if var.get(NODE_ALLOWED_LIST) != "NONE":
                print(
                    " " * 8
                    + "| %s: %s"
                    % (
                        NODE_ALLOWED_LIST,
                        "(%s)" % ("; ".join(var.get(NODE_ALLOWED_LIST))),
                    )
                )

            if var.get(NODE_ALLOWED_RANGE) != "NONE":
                r = var.get(NODE_ALLOWED_RANGE)
                print(
                    " " * 8
                    + "| %s: min=%s, max=%s, step=%s"
                    % (
                        NODE_ALLOWED_RANGE,
                        r.get(NODE_MIN),
                        r.get(NODE_MAX),
                        r.get(NODE_STEP),
                    )
                )

    def __str__(self) -> str:
        s = "[>] SCPD:\n"
        for x in self:
            if x == NODE_ACTION_LIST:
                s += '\t|-Action-List:\n'
                for a in self[x]:
                    s += self.format_action(a) + '\n'
            elif x == NODE_STATE_TABLE:
                s += '\t|-Service-state-Table:\n'
                for v in self[x]:
                    s += self.format_var(v) + '\n'
            else:
                s += '\t| %s: %s\n' % (x, self[x])
        return s

    def format_action(self, _a: Action, indent='\t\t'):
        if _a:
            param = []
            out = []
            if not _a.get(NODE_ARGUMENT_LIST):
                print('%s+ %s():\n%sreturn None\n' % (indent, _a.get(NODE_NAME), indent*2))
            else:
                for arg in _a.get(NODE_ARGUMENT_LIST):
                    d = arg.get(NODE_DIRECTION) 
                    if d == 'in':
                        var = ""
                        if arg.get(NODE_RELATED_VARIABLE):
                            var = ': ' + arg.get(NODE_RELATED_VARIABLE)
                        param.append('%s%s' % (arg.get(NODE_NAME), var))
                    else: #'out'
                        var = ""
                        if arg.get(NODE_RELATED_VARIABLE):
                            var = ': ' + arg.get(NODE_RELATED_VARIABLE)
                        out.append('%s%s' % (arg.get(NODE_NAME), var))
                
                param = param if len(param) <= 3 else [param[0], param[1], '...']
                out = out if len(out) <= 3 else [out[0], out[1], '...'] 
                if len(out) == 0:
                    out = ['None']

                if len(out) > 1:
                    return '%s+ %s(%s):\n%sreturn [%s]\n' % (indent, _a.get(NODE_NAME), ', '.join(param), indent*2, out[0])
                else:
                    return '%s+ %s(%s):\n%sreturn [%s]\n' % (indent, _a.get(NODE_NAME), ', '.join(param), indent*2, ', '.join(out))

    #TODO format all stored vars
    def format_var(self, _v, indent='\t\t'):
        try:
            d = _v[NODE_DEFAULT_VALUE]
        except:
            return '%s+ %s: %s' % (indent, _v[NODE_NAME], _v[NODE_DATA_TYPE])
        else:
            return '%s+ %s: %s (default=%s)' % (indent, _v[NODE_NAME], _v[NODE_DATA_TYPE], d)

