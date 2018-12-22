from helpers import *
from unreal_engine.classes import (Blueprint, K2Node_FunctionResult, K2Node_MakeArray as K2Node_MakeArray, K2Node_Event, K2Node_MakeStruct,
    KismetSystemLibrary as KSL, KismetTextLibrary as KTL, KismetStringLibrary as KStrLib)
from unreal_engine import EdGraphPin, UObject, UScriptStruct

def FindBP(path, open=False):
    bp = ue.load_object(Blueprint, path)
    if bp and open:
        ue.open_editor_for_asset(bp)
    return bp

class NodeWrapper:
    def __init__(self, node):
        self._pins = {}
        self._node = node
        self.RefreshPins()

    def RefreshPins(self):
        pins = {}
        for p in self._node.node_pins():
            pins[p.name] = p
        #log('PINS:', self._node, pins.keys())
        self._pins = pins

    def __getattr__(self, k): # TODO: make get/set on pins case insensitive
        try:
            return self._pins[k]
        except KeyError:
            return super().__getattr__(k)

    def __setattr__(self, k, v):
        if k.startswith('_'):
            return super().__setattr__(k,v)

        pin = self._pins[k]
        if type(v) is EdGraphPin:
            # setting a pin to another pin triggers a connect
            #log('connecting', pin, 'to', v)
            pin.make_link_to(v)
        elif type(v) is NodeWrapper:
            # TODO: if pin is an output pin and v has a single input pin, or pin is an input pin and v has a single
            # output pin, automatically connect them
            raise Exception('Pin', pin, 'must be connected to a pin, not a node wrapper')
        else:
            # otherwise triggers setting its default value
            #log('setting default', pin, v)
            pin.default_value = str(v)
            self._node.node_pin_default_value_changed(pin)

def ObjToStr(o):
    if type(o) is FVector:
        return '%.08f, %.08f, %.08f' % (o.x, o.y, o.z)
    return str(o)

from unreal_engine.structs import Vector as StructVector # this is *not* FVector
def MakeArray(graph, values, pos=None):
    if pos is None:
        pos = graph.graph_get_good_place_for_new_node()
    node = graph.graph_add_node(K2Node_MakeArray, *pos)
    node.NumInputs = len(values)
    node.node_reconstruct()
    sub = None
    t = type(values[0])
    if t is int:
        pinType = 'int'
    elif t is bool:
        pinType = 'bool'
    elif t is str:
        pinType = 'string'
    elif t is FVector:
        pinType = 'struct'
        sub = StructVector
    else:
        assert 0, t
    for i, val in enumerate(values):
        pin = node.node_find_pin('[%d]' % i)
        pin.category = pinType
        if sub is not None:
            pin.sub_category = sub
        pin.default_value = ObjToStr(val)
        node.node_pin_default_value_changed(pin)
    w = NodeWrapper(node)
    w.Array.category = pinType
    if sub is not None:
        w.Array.sub_category = sub
    return w

def MakeConnectedArray(graph, category, subcategory, pins, pos=None):
    '''like MakeArray, but instead of literals, it connects the pins to the given inputs'''
    if pos is None:
        pos = graph.graph_get_good_place_for_new_node()
    node = graph.graph_add_node(K2Node_MakeArray, *pos)
    node.NumInputs = len(pins)
    node.node_reconstruct()
    for i, otherPin in enumerate(pins):
        pin = node.node_find_pin('[%d]' % i)
        pin.category = category
        pin.sub_category = subcategory
        pin.make_link_to(otherPin)
    node = NodeWrapper(node)
    node.Array.category = category
    node.Array.sub_category = subcategory
    return node

def MakeLiteral(graph, value, pos=None):
    if pos is None:
        pos = graph.graph_get_good_place_for_new_node()
    if type(value) is int:
        func = KSL.MakeLiteralInt
        default = str(value)
    elif type(value) is float:
        func = KSL.MakeLiteralFloat
        default = '%.05f' % value
    elif type(value) is str:
        func = KSL.MakeLiteralString
        default = value
    else:
        assert 0, (value, type(value))
    node = graph.graph_add_node_call_function(func)
    w = NodeWrapper(node)
    w.Value = default
    return w

def MakeCall(graph, func, pos=None):
    if pos is None:
        pos = graph.graph_get_good_place_for_new_node()
    node = graph.graph_add_node_call_function(func)
    return NodeWrapper(node)

def GetVariable(graph, name):
    return NodeWrapper(graph.graph_add_node_variable_get(name))

from unreal_engine.classes import Blueprint, K2Node_DynamicCast, Actor, Object
from unreal_engine.structs import EdGraphPinType
from unreal_engine.enums import EEdGraphPinDirection
def MakeArgsStr(graph, *args):
    # args is a list of (pin, convert func) entries
    # TODO: auto detect instead!
    array = MakeArray(graph, ['dummy'] * len(args))
    for i, (pin, converter) in enumerate(args):
        convert = MakeCall(graph, converter)
        convert.input = pin
        setattr(array, '[%d]' % i, convert.output)
    join = MakeCall(graph, KStrLib.JoinStringArray)
    join.SourceArray = array.Array
    join.Separator = ','
    return join

def TestRecorderNote(graph, who, action, argsPin, executePin):
    '''adds a call to TestRecorder.Note, wires it up, and returns the wrapped node'''
    node = MakeCall(graph, TestRecorder.Note)
    node.self = GetVariable(graph, 'Recorder').Recorder
    node.who = who
    node.action = action
    node.args = argsPin
    node.execute = executePin
    return node

def GetFunctionGraph(bp, name):
    for graph in bp.FunctionGraphs:
        if graph.get_name() == name:
            return graph
    assert 0, 'Function %s not found' % name

def GetEventNode(bp, name):
    for node in bp.UberGraphPages[0].Nodes:
        if node.is_a(K2Node_Event) and node.EventReference.MemberName == name:
            return NodeWrapper(node)
    assert 0, 'Event %s not found' % name

def GetReturnNode(graph):
    for node in graph.Nodes:
        if node.is_a(K2Node_FunctionResult):
            return NodeWrapper(node)
    assert 0, 'No return node found'

def MakeTestStruct(graph, name, number, pos=None):
    if pos is None:
        pos = graph.graph_get_good_place_for_new_node()
    node = graph.graph_add_node(K2Node_MakeStruct, *pos)
    node.StructType = TestStruct
    node.node_reconstruct()
    node = NodeWrapper(node)
    node.name = name
    node.number = number
    return node

Utils = FindBP('/Game/Utils.Utils').GeneratedClass
from unreal_engine.classes import TestRecorder, TestActor, ParamActor
from unreal_engine.structs import TestStruct

if 0:
    # StructInOutRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'StructInOutRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.inStructs, Utils.StrStructArray))
    recvNote = TestRecorderNote(graph, 'StructInOutRet', 'recv', argsStr.ReturnValue, entry.then)
    structs = []
    for name, num in ('Spring',5001), ('Summer',-5002), ('Fall',5003),('Winter',-5004):
        structs.append(MakeTestStruct(graph, name, num).TestStruct)
    outArray = MakeConnectedArray(graph, 'struct', TestStruct, structs)
    outF = MakeLiteral(graph, 101.125)
    structs = []
    for name, num in ('Brighton',16),('Alta',18),('Solitude',20):
        structs.append(MakeTestStruct(graph, name, num).TestStruct)
    retArray = MakeConnectedArray(graph, 'struct', TestStruct, structs)
    argsStr = MakeArgsStr(graph, (outArray.Array, Utils.StrStructArray), (outF.ReturnValue, Utils.StrFloat), (retArray.Array, Utils.StrStructArray))
    sendNote = TestRecorderNote(graph, 'StructInOutRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.outStructs = outArray.Array
    ret.of = outF.ReturnValue
    ret.ReturnValue = retArray.Array

if 0:
    # TestStructInOutRet
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestStructInOutRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 6357)
    structs = []
    for name, num in ('Dell',107), ('HP', 1000), ('Razor', 201):
        structs.append(MakeTestStruct(graph, name, num).TestStruct)
    a = MakeConnectedArray(graph, 'struct', TestStruct, structs)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (a.Array, Utils.StrStructArray))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StructInOutRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.inStructs = a.Array
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.outStructs, Utils.StrStructArray), (taCall.of, Utils.StrFloat), (taCall.ReturnValue, Utils.StrStructArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # StructRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'StructRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'StructRet', 'recv', argsStr.ReturnValue, entry.then)
    structs = []
    for name, num in ('Red', 101), ('Blue', 102), ('Green', 103), ('Orange', 104):
        structs.append(MakeTestStruct(graph, name, num).TestStruct)
    array = MakeConnectedArray(graph, 'struct', TestStruct, structs)
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrStructArray))
    sendNote = TestRecorderNote(graph, 'StructRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.ReturnValue = array.Array

if 0:
    # TestStructRet
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestStructRet')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestStructRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 10242048)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StructRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.ReturnValue, Utils.StrStructArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # StructOut
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'StructOut')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'StructOut', 'recv', argsStr.ReturnValue, entry.then)
    structs = []
    for name, num in ('Monday', 5), ('toozdee', 10), ('Wed', 15), ('Thirsty', 20):
        structs.append(MakeTestStruct(graph, name, num).TestStruct)
    array = MakeConnectedArray(graph, 'struct', TestStruct, structs)
    of = MakeLiteral(graph, 9.895)
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrStructArray), (of.ReturnValue, Utils.StrFloat))
    sendNote = TestRecorderNote(graph, 'StructOut', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.structs = array.Array
    ret.of = of.ReturnValue

if 0:
    # TestStructOut
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestStructOut')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestStructOut')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 1234567)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StructOut)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.structs, Utils.StrStructArray), (taCall.of, Utils.StrFloat))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # StructIn
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = bp.UberGraphPages[0]
    entry = GetEventNode(bp, 'StructIn')
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.structs, Utils.StrStructArray), (entry.f, Utils.StrFloat))
    recvNote = TestRecorderNote(graph, 'StructIn', 'recv', argsStr.ReturnValue, entry.then)
    sendNote = TestRecorderNote(graph, 'StructIn', 'send', 'None', recvNote.then)

if 0:
    # TestStructIn
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestStructIn')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestStructIn')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 1887)
    structs = []
    for name, num in ('Fingers', 10), ('Toes', 11), ('knees', 12), ('elboWS', 99):
        structs.append(MakeTestStruct(graph, name, num).TestStruct)
    array = MakeConnectedArray(graph, 'struct', TestStruct, structs)
    f = MakeLiteral(graph, -271.122)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (array.Array, Utils.StrStructArray), (f.ReturnValue, Utils.StrFloat))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StructIn)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.structs = array.Array
    taCall.f = f.ReturnValue
    taCall.execute = preNote.then
    TestRecorderNote(graph, 'tester', 'recv', 'None', taCall.then)

if 0:
    # ActorInOutRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'ActorInOutRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.inActors, Utils.StrActorArray))
    recvNote = TestRecorderNote(graph, 'ActorInOutRet', 'recv', argsStr.ReturnValue, entry.then)
    prevLink = recvNote.then
    actors = []
    for name in 'Up Down Left Right'.split():
        spawn = MakeCall(graph, ParamActor.SpawnWithName)
        spawn.withName = name
        spawn.execute = prevLink
        prevLink = spawn.then
        actors.append(spawn.ReturnValue)
    outArray = MakeConnectedArray(graph, 'object', ParamActor, actors)
    outF = MakeLiteral(graph, 98.715)
    actors = []
    for name in 'North South East wEsT'.split():
        spawn = MakeCall(graph, ParamActor.SpawnWithName)
        spawn.withName = name
        spawn.execute = prevLink
        prevLink = spawn.then
        actors.append(spawn.ReturnValue)
    retArray = MakeConnectedArray(graph, 'object', ParamActor, actors)
    argsStr = MakeArgsStr(graph, (outArray.Array, Utils.StrActorArray), (outF.ReturnValue, Utils.StrFloat), (retArray.Array, Utils.StrActorArray))
    sendNote = TestRecorderNote(graph, 'ActorInOutRet', 'send', argsStr.ReturnValue, prevLink)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.outActors = outArray.Array
    ret.of = outF.ReturnValue
    ret.ReturnValue = retArray.Array

if 0:
    # TestActorInOutRet
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestActorInOutRet')
    entry = NodeWrapper(graph.Nodes[0])
    prevLink = entry.then
    i = MakeLiteral(graph, 8675309)
    actors = []
    for name in 'Larry Curly Moe'.split():
        spawn = MakeCall(graph, ParamActor.SpawnWithName)
        spawn.withName = name
        spawn.execute = prevLink
        prevLink = spawn.then
        actors.append(spawn.ReturnValue)
    array = MakeConnectedArray(graph, 'object', ParamActor, actors)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (array.Array, Utils.StrActorArray))
    sendNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, prevLink)
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.ActorInOutRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.inActors = array.Array
    taCall.execute = sendNote.then
    argsStr = MakeArgsStr(graph, (taCall.outActors, Utils.StrActorArray), (taCall.of, Utils.StrFloat), (taCall.ReturnValue, Utils.StrActorArray))
    recvNote = TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)
    destroy = MakeCall(graph, ParamActor.DestroyActors)
    destroy.execute = recvNote.then
    destroy.actors = array.Array
    d2 = MakeCall(graph, ParamActor.DestroyActors)
    d2.execute = destroy.then
    d2.actors = taCall.outActors
    d3 = MakeCall(graph, ParamActor.DestroyActors)
    d3.execute = d2.then
    d3.actors = taCall.ReturnValue

if 0:
    # ActorRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'ActorRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'ActorRet', 'recv', argsStr.ReturnValue, entry.then)
    prevLink = recvNote.then
    actors = []
    for name in 'Luke Han Leia Lando Bobba'.split():
        spawn = MakeCall(graph, ParamActor.SpawnWithName)
        spawn.withName = name
        spawn.execute = prevLink
        prevLink = spawn.then
        actors.append(spawn.ReturnValue)
    array = MakeConnectedArray(graph, 'object', ParamActor, actors)
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrActorArray))
    sendNote = TestRecorderNote(graph, 'ActorRet', 'send', argsStr.ReturnValue, prevLink)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.ReturnValue = array.Array

if 0:
    # TestActorRet
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestActorRet')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestActorRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 311111)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.ActorRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.ReturnValue, Utils.StrActorArray))
    recvNote = TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)
    destroy = MakeCall(graph, ParamActor.DestroyActors)
    destroy.execute = recvNote.then
    destroy.actors = taCall.ReturnValue

if 0:
    # ActorOut
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'ActorOut')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'ActorOut', 'recv', argsStr.ReturnValue, entry.then)
    prevLink = recvNote.then
    actors = []
    for name in 'Joseph Hyrum Alvin'.split():
        spawn = MakeCall(graph, ParamActor.SpawnWithName)
        spawn.withName = name
        spawn.execute = prevLink
        prevLink = spawn.then
        actors.append(spawn.ReturnValue)
    array = MakeConnectedArray(graph, 'object', ParamActor, actors)
    of = MakeLiteral(graph, 254.061)
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrActorArray), (of.ReturnValue, Utils.StrFloat))
    sendNote = TestRecorderNote(graph, 'ActorOut', 'send', argsStr.ReturnValue, prevLink)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.actors = array.Array
    ret.of = of.ReturnValue

if 0:
    # TestActorOut
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestActorOut')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestActorOut')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 7455)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.ActorOut)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.actors, Utils.StrActorArray), (taCall.of, Utils.StrFloat))
    recvNote = TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)
    destroy = MakeCall(graph, ParamActor.DestroyActors)
    destroy.execute = recvNote.then
    destroy.actors = taCall.actors

if 0:
    # ActorIn
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = bp.UberGraphPages[0]
    entry = GetEventNode(bp, 'ActorIn')
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.actors, Utils.StrActorArray), (entry.f, Utils.StrFloat))
    recvNote = TestRecorderNote(graph, 'ActorIn', 'recv', argsStr.ReturnValue, entry.then)
    sendNote = TestRecorderNote(graph, 'ActorIn', 'send', 'None', recvNote.then)

if 0:
    # TestActorIn
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestActorIn')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestActorIn')
    entry = NodeWrapper(graph.Nodes[0])
    prevLink = entry.then
    actors = []
    for name in 'Joe Fred Jared Ed'.split():
        spawn = MakeCall(graph, ParamActor.SpawnWithName)
        spawn.withName = name
        spawn.execute = prevLink
        prevLink = spawn.then
        actors.append(spawn.ReturnValue)

    i = MakeLiteral(graph, 13)
    array = MakeConnectedArray(graph, 'object', ParamActor, actors)
    f = MakeLiteral(graph, -689.123)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (array.Array, Utils.StrActorArray), (f.ReturnValue, Utils.StrFloat))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, prevLink)
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.ActorIn)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.actors = array.Array
    taCall.f = f.ReturnValue
    taCall.execute = preNote.then
    recvNote = TestRecorderNote(graph, 'tester', 'recv', 'None', taCall.then)
    destroy = MakeCall(graph, ParamActor.DestroyActors)
    destroy.execute = recvNote.then
    destroy.actors = array.Array

if 0:
    # StringInOutRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'StringInOutRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.inStrings, Utils.StrStringArray))
    recvNote = TestRecorderNote(graph, 'StringInOutRet', 'recv', argsStr.ReturnValue, entry.then)
    outArray = MakeArray(graph, ['Origin','Rebates','Foreseen','Abner'])
    outF = MakeLiteral(graph, 77.115)
    retArray = MakeArray(graph, ['Battery', 'Mouse', 'Pad', 'Charger', 'Cord'])
    argsStr = MakeArgsStr(graph, (outArray.Array, Utils.StrStringArray), (outF.ReturnValue, Utils.StrFloat), (retArray.Array, Utils.StrStringArray))
    sendNote = TestRecorderNote(graph, 'StringInOutRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.outStrings = outArray.Array
    ret.of = outF.ReturnValue
    ret.ReturnValue = retArray.Array

if 0:
    # TestStringInOutRet
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestStringInOutRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 73716)
    a = MakeArray(graph, ['One','Two','Three','Four','Five','Six'])
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (a.Array, Utils.StrStringArray))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StringInOutRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.inStrings = a.Array
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.outStrings, Utils.StrStringArray), (taCall.of, Utils.StrFloat), (taCall.ReturnValue, Utils.StrStringArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # StringRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'StringRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'StringRet', 'recv', argsStr.ReturnValue, entry.then)
    array = MakeArray(graph, ['Enero', 'Febrero', 'Marzo', 'Abril'])
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrStringArray))
    sendNote = TestRecorderNote(graph, 'StringRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.ReturnValue = array.Array

if 0:
    # TestStringRet
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestStringRet')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestStringRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 17761)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StringRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.ReturnValue, Utils.StrStringArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # StringOut
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'StringOut')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'StringOut', 'recv', argsStr.ReturnValue, entry.then)
    array = MakeArray(graph, ['Jan', 'February', 'MaRzO'])
    of = MakeLiteral(graph, -113.311)
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrStringArray), (of.ReturnValue, Utils.StrFloat))
    sendNote = TestRecorderNote(graph, 'StringOut', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.strings = array.Array
    ret.of = of.ReturnValue

if 0:
    # TestStringOut
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestStringOut')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestStringOut')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 12321)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StringOut)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.strings, Utils.StrStringArray), (taCall.of, Utils.StrFloat))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # StringIn
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = bp.UberGraphPages[0]
    entry = GetEventNode(bp, 'StringIn')
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.strings, Utils.StrStringArray), (entry.f, Utils.StrFloat))
    recvNote = TestRecorderNote(graph, 'StringIn', 'recv', argsStr.ReturnValue, entry.then)
    sendNote = TestRecorderNote(graph, 'StringIn', 'send', 'None', recvNote.then)

if 0:
    # TestStringIn
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestStringIn')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestStringIn')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 786)
    array = MakeArray(graph, ['Rachael', 'Jacob', 'Nathan', 'Adam'])
    f = MakeLiteral(graph, 3.142)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (array.Array, Utils.StrStringArray), (f.ReturnValue, Utils.StrFloat))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.StringIn)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.strings = array.Array
    taCall.f = f.ReturnValue
    taCall.execute = preNote.then
    TestRecorderNote(graph, 'tester', 'recv', 'None', taCall.then)

if 0:
    # VectorInOutRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'VectorInOutRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.inVectors, Utils.StrVectorArray))
    recvNote = TestRecorderNote(graph, 'VectorInOutRet', 'recv', argsStr.ReturnValue, entry.then)

    outArray = MakeArray(graph, [FVector(1.111,2.222,3.333), FVector(4.444,5.555,6.666)])
    outF = MakeLiteral(graph, 1151.966)
    retArray = MakeArray(graph, [FVector(100.000,200.000,300.000), FVector(400.000,500.000,600.000), FVector(10.000,20.000,30.000), FVector(40.000,50.000,60.000)])
    argsStr = MakeArgsStr(graph, (outArray.Array, Utils.StrVectorArray), (outF.ReturnValue, Utils.StrFloat), (retArray.Array, Utils.StrVectorArray))
    sendNote = TestRecorderNote(graph, 'VectorInOutRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.outVectors = outArray.Array
    ret.of = outF.ReturnValue
    ret.ReturnValue = retArray.Array

if 0:
    # TestVectorInOutRet
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestVectorInOutRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 99411)
    a = MakeArray(graph, [FVector(10,11,12),FVector(13,14,15),FVector(16,17,18),FVector(19,20,-21)])
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (a.Array, Utils.StrVectorArray))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.VectorInOutRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.inVectors = a.Array
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.outVectors, Utils.StrVectorArray), (taCall.of, Utils.StrFloat), (taCall.ReturnValue, Utils.StrVectorArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # VectorRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'VectorRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'VectorRet', 'recv', argsStr.ReturnValue, entry.then)
    array = MakeArray(graph, [FVector(11.225,-5.0,33.333), FVector(5,4,3), FVector(-1,-10,-100)])
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrVectorArray))
    sendNote = TestRecorderNote(graph, 'VectorRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.ReturnValue = array.Array

if 0:
    # TestVectorRet
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestVectorRet')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestVectorRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 5110)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.VectorRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.ReturnValue, Utils.StrVectorArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # VectorOut
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'VectorOut')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'VectorOut', 'recv', argsStr.ReturnValue, entry.then)
    array = MakeArray(graph, [FVector(5.5, 4.5, 3.5),FVector(-1.2, -10, 5000),FVector(17.125, -105.177, 32.111)])
    of = MakeLiteral(graph, 99.101)
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrVectorArray), (of.ReturnValue, Utils.StrFloat))
    sendNote = TestRecorderNote(graph, 'VectorOut', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.vectors = array.Array
    ret.of = of.ReturnValue

if 0:
    # TestVectorOut
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestVectorOut')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestVectorOut')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 7777)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.VectorOut)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.vectors, Utils.StrVectorArray), (taCall.of, Utils.StrFloat))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # VectorIn
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = bp.UberGraphPages[0]
    entry = GetEventNode(bp, 'VectorIn')
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.vectors, Utils.StrVectorArray), (entry.f, Utils.StrFloat))
    recvNote = TestRecorderNote(graph, 'VectorIn', 'recv', argsStr.ReturnValue, entry.then)
    sendNote = TestRecorderNote(graph, 'VectorIn', 'send', 'None', recvNote.then)

if 0:
    # TestVectorIn
    bp = FindBP('/Game/BTester.BTester')
    try:
        GetFunctionGraph(bp, 'TestVectorIn')
        raise Exception('Delete function first!')
    except AssertionError:
        pass
    graph = ue.blueprint_add_function(bp, 'TestVectorIn')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 3819)
    array = MakeArray(graph, [FVector(1,2,3),FVector(4,5,6)])
    f = MakeLiteral(graph, 117.880)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (array.Array, Utils.StrVectorArray), (f.ReturnValue, Utils.StrFloat))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.VectorIn)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.vectors = array.Array
    taCall.f = f.ReturnValue
    taCall.execute = preNote.then
    TestRecorderNote(graph, 'tester', 'recv', 'None', taCall.then)

if 0:
    # BoolInOutRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    graph = GetFunctionGraph(bp, 'BoolInOutRet')
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt), (entry.inBools, Utils.StrBoolArray))
    recvNote = TestRecorderNote(graph, 'BoolInOutRet', 'recv', argsStr.ReturnValue, entry.then)
    outArray = MakeArray(graph, [True, False, False, True, True, True, True, True, False])
    outF = MakeLiteral(graph, 1125.865)
    retArray = MakeArray(graph, [True, True, False, False, False, True, False, False, True, True])
    argsStr = MakeArgsStr(graph, (outArray.Array, Utils.StrBoolArray), (outF.ReturnValue, Utils.StrFloat), (retArray.Array, Utils.StrBoolArray))
    sendNote = TestRecorderNote(graph, 'BoolInOutRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.outBools = outArray.Array
    ret.of = outF.ReturnValue
    ret.ReturnValue = retArray.Array

if 0:
    # TestBoolInOutRet
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestBoolInOutRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 32711)
    a = MakeArray(graph, [False, False, True, False, False, True, False, True, True, True])
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (a.Array, Utils.StrBoolArray))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.BoolInOutRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.inBools = a.Array
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.outBools, Utils.StrBoolArray), (taCall.of, Utils.StrFloat), (taCall.ReturnValue, Utils.StrBoolArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # BoolRet
    bp = FindBP('/Game/BTestActor.BTestActor')
    for graph in bp.FunctionGraphs:
        if graph.get_name() == 'BoolRet':
            break
    else:
        graph = None
    entry = NodeWrapper(graph.Nodes[0])
    argsStr = MakeArgsStr(graph, (entry.i, Utils.StrInt))
    recvNote = TestRecorderNote(graph, 'BoolRet', 'recv', argsStr.ReturnValue, entry.then)
    array = MakeArray(graph, [True, False, True, False, False, True, True])
    argsStr = MakeArgsStr(graph, (array.Array, Utils.StrBoolArray))
    sendNote = TestRecorderNote(graph, 'BoolRet', 'send', argsStr.ReturnValue, recvNote.then)
    ret = GetReturnNode(graph)
    ret.execute = sendNote.then
    ret.ReturnValue = array.Array

if 0:
    # TestBoolRet
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestBoolRet')
    entry = graph.Nodes[0]
    i = MakeLiteral(graph, 6991)
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.BoolRet)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then
    argsStr = MakeArgsStr(graph, (taCall.ReturnValue, Utils.StrBoolArray))
    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # TestBoolOut
    # Add a test node
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestBoolOut')
    entry = graph.Nodes[0]

    # build args
    i = MakeLiteral(graph, 81)

    # make args string
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt))

    # note in test recorder
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))

    # call func
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.BoolOut)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.execute = preNote.then

    # combine result
    argsStr = MakeArgsStr(graph, (taCall.bools, Utils.StrBoolArray), (taCall.of, Utils.StrFloat))

    TestRecorderNote(graph, 'tester', 'recv', argsStr.ReturnValue, taCall.then)

if 0:
    # TestBoolIn
    # Add a test node
    bp = FindBP('/Game/BTester.BTester')
    graph = ue.blueprint_add_function(bp, 'TestBoolIn')
    entry = graph.Nodes[0]

    # build args
    i = MakeLiteral(graph, 44)
    a = MakeArray(graph, [True, False, False, True, True])
    f = MakeLiteral(graph, 202.511)

    # make args string
    argsStr = MakeArgsStr(graph, (i.ReturnValue, Utils.StrInt), (a.Array, Utils.StrBoolArray), (f.ReturnValue, Utils.StrFloat))

    # note in test recorder
    preNote = TestRecorderNote(graph, 'tester', 'send', argsStr.ReturnValue, entry.node_find_pin('then'))

    # call func
    ta = GetVariable(graph, 'TestActor')
    taCall = MakeCall(graph, TestActor.BoolIn)
    taCall.self = ta.TestActor
    taCall.i = i.ReturnValue
    taCall.bools = a.Array
    taCall.f = f.ReturnValue
    taCall.execute = preNote.then

    # combine result
    # (not needed here)

    TestRecorderNote(graph, 'tester', 'recv', 'None', taCall.then)

