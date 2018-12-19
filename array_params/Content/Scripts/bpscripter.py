from helpers import *
from unreal_engine.classes import Blueprint, K2Node_MakeArray as K2Node_MakeArray, K2Node_Event, KismetSystemLibrary as KSL, KismetTextLibrary as KTL, KismetStringLibrary as KStrLib
from unreal_engine import EdGraphPin

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
            log('setting default', pin, v)
            pin.default_value = str(v)
            self._node.node_pin_default_value_changed(pin)

def MakeArray(graph, values, pos=None):
    if pos is None:
        pos = graph.graph_get_good_place_for_new_node()
    node = graph.graph_add_node(K2Node_MakeArray, *pos)
    node.NumInputs = len(values)
    node.node_reconstruct()
    t = type(values[0])
    if t is int:
        pinType = 'int'
    elif t is bool:
        pinType = 'bool'
    elif t is str:
        pinType = 'string'
    else:
        assert 0, t
    for i, val in enumerate(values):
        pin = node.node_find_pin('[%d]' % i)
        pin.category = pinType
        pin.default_value = str(val)
        node.node_pin_default_value_changed(pin)
    w = NodeWrapper(node)
    w.Array.category = pinType
    return w

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

Utils = FindBP('/Game/Utils.Utils').GeneratedClass
from unreal_engine.classes import TestRecorder, TestActor

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
tr = GetVariable(graph, 'TestRecorder')
preNote = MakeCall(graph, TestRecorder.Note)
preNote.self = tr.TestRecorder
preNote.who = 'tester'
preNote.action = 'send'
preNote.args = argsStr.ReturnValue
preNote.execute = entry.node_find_pin('then')

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

# pass to test recorder
node = MakeCall(graph, TestRecorder.Note)
node.self = tr.TestRecorder
node.who = 'tester'
node.action = 'recv'
node.args = 'None'
node.execute = taCall.then

if 0:
    Utils = FindBP('/Game/Utils.Utils').GeneratedClass
    bp = FindBP('/Game/BTestActor.BTestActor', True)
    log(bp)

    ug = bp.UberGraphPages[0]
    recorder = GetVariable(ug, 'Recorder')
    note = MakeCall(ug, TestRecorder.Note)
    note.self = recorder.Recorder
    note.who = 'barney'
    note.action = 'recv'

if 0:
    convert = MakeCall(ug, Utils.Convert_I_IA_F)
    convert.i = MakeLiteral(ug, 32).ReturnValue
    convert.ia = MakeArray(ug, [1000, 500, 400, 300, 200]).Array
    convert.f = MakeLiteral(ug, 12.34).ReturnValue

    totext = MakeCall(ug, KTL.Conv_StringToText)
    totext.InString = convert.s
    printtext = MakeCall(ug, KSL.PrintText)
    printtext.InText = totext.ReturnValue

if 0:

    import unittest
    import unreal_engine as ue
    from unreal_engine.classes import Actor, Character
    from unreal_engine import FVector
    import time
    import math

    class TestBlueprint(unittest.TestCase):

        def setUp(self):
            self.world = ue.get_editor_world()
            self.random_string = str(int(time.time()))


        def tearDown(self):
            ue.allow_actor_script_execution_in_editor(False)

        def test_creation(self):
            new_blueprint = ue.create_blueprint(Actor, '/Game/Tests/Blueprints/Test0_' + self.random_string)
            ue.log(new_blueprint.ParentClass)
            self.assertEqual(new_blueprint.ParentClass, Actor)
            self.assertNotEqual(new_blueprint.ParentClass, Character)

        def test_spawn(self):
            new_blueprint = ue.create_blueprint(Character, '/Game/Tests/Blueprints/Test1_' + self.random_string)
            new_actor = self.world.actor_spawn(new_blueprint.GeneratedClass)
            self.assertTrue(new_actor.is_a(Character))

        def test_variable(self):
            new_blueprint = ue.create_blueprint(Character, '/Game/Tests/Blueprints/Test2_' + self.random_string)
            ue.blueprint_add_member_variable(new_blueprint, 'TestValue', 'int')
            ue.compile_blueprint(new_blueprint)
            new_actor = self.world.actor_spawn(new_blueprint.GeneratedClass)
            new_actor.TestValue = 17
            self.assertEqual(new_actor.get_property('TestValue'), 17)

        def test_event(self):
            new_blueprint = ue.create_blueprint(Character, '/Game/Tests/Blueprints/Test3_' + self.random_string)
            uber_page = new_blueprint.UberGraphPages[0]
            x, y = uber_page.graph_get_good_place_for_new_node()
            test_event = uber_page.graph_add_node_custom_event('TestEvent', x, y)
            x, y = uber_page.graph_get_good_place_for_new_node()
            node_set_actor_location = uber_page.graph_add_node_call_function(Actor.K2_SetActorLocation, x, y)
            test_event.node_find_pin('then').make_link_to(node_set_actor_location.node_find_pin('execute'))
            node_set_actor_location.node_find_pin('NewLocation').default_value = '17,30,22'
            ue.compile_blueprint(new_blueprint)
            new_actor = self.world.actor_spawn(new_blueprint.GeneratedClass)
            self.assertEqual(new_actor.get_actor_location(), FVector(0, 0, 0))
            ue.allow_actor_script_execution_in_editor(True)
            new_actor.TestEvent()
            self.assertEqual(new_actor.get_actor_location(), FVector(17, 30, 22))


    if __name__ == '__main__':
        unittest.main(exit=False)

        import unreal_engine as ue
        from unreal_engine.classes import Blueprint, K2Node_DynamicCast, Actor, Object
        from unreal_engine.structs import EdGraphPinType
        from unreal_engine.enums import EEdGraphPinDirection

        bp_foo = ue.load_object(Blueprint, '/Game/Foo.Foo')
        bp_bar = ue.load_object(Blueprint, '/Game/Bar.Bar')

        cast_node = K2Node_DynamicCast()
        cast_node.TargetType = bp_bar.GeneratedClass

        graph = ue.blueprint_add_function(bp_foo, 'FooCaster')
        func = graph.Nodes[0]

        pin_type = EdGraphPinType(PinCategory = 'object', PinSubCategoryObject=Actor)
        pin = func.node_create_pin(EEdGraphPinDirection.EGPD_Input, pin_type, 'Arg001')


        graph.graph_add_node(cast_node, 600, 0)

        cast_node.node_find_pin('Object').category = 'object'
        cast_node.node_find_pin('Object').sub_category = Object

        pin.make_link_to(cast_node.node_find_pin('Object'))
        func.node_find_pin('then').make_link_to(cast_node.node_find_pin('execute'))

        ue.compile_blueprint(bp_foo)

# ----------------------

    import unreal_engine as ue

    from unreal_engine.classes import Material, BlueprintFactory, Blueprint, Actor, Texture2D, SkeletalMesh
    from unreal_engine.structs import EdGraphPinType, Vector, Rotator, EdGraphTerminalType
    from unreal_engine.enums import EPinContainerType

    import time

    bp = ue.create_blueprint(Actor, '/Game/FooActor' + str(int(time.time())))

    pin = EdGraphPinType(PinCategory='object', PinSubCategoryObject=Material)
    ue.blueprint_add_member_variable(bp, 'TestMat', pin, None, '/Engine/MapTemplates/Materials/BasicAsset03.BasicAsset03')

    pin = EdGraphPinType(PinCategory='class', PinSubCategoryObject=Texture2D)
    ue.blueprint_add_member_variable(bp, 'TestTextureClass', pin)

    pin = EdGraphPinType(PinCategory='struct',PinSubCategoryObject=Vector)
    ue.blueprint_add_member_variable(bp, 'TestVector', pin, None, '17,22,30')

    pin = EdGraphPinType(PinCategory='struct',PinSubCategoryObject=Rotator,ContainerType=EPinContainerType.Array)
    ue.blueprint_add_member_variable(bp, 'TestRotator', pin, None, '((Pitch=0.000000,Yaw=3.000000,Roll=0.000000),(Pitch=1.000000,Yaw=0.000000,Roll=0.000000))')

    pin = EdGraphPinType(PinCategory='string',ContainerType=EPinContainerType.Map,PinValueType=EdGraphTerminalType(TerminalCategory='object',TerminalSubCategoryObject=SkeletalMesh))
    ue.blueprint_add_member_variable(bp, 'TestMap', pin, None, '(("firstKey", SkeletalMesh\'"/Game/Skel001"\'),("secondKey", SkeletalMesh\'"/Game/Skel002"\'))')

    ue.compile_blueprint(bp)

    ue.open_editor_for_asset(bp)

# ---------------------


    import unreal_engine as ue
    from unreal_engine.classes import BlueprintFactory, DirectionalLightComponent, K2Node_Event

    import time

# create new blueprint from factory
    bpFactory = BlueprintFactory()
    bp = bpFactory.factory_create_new('/Game/test' + str(int(time.time())))

# add intensity variable
    intensity = ue.blueprint_add_member_variable(bp, 'intensity', 'float')
# set its visibility to True
    ue.blueprint_set_variable_visibility(bp, 'intensity', True)

# add directional light component
    directLightComponent = ue.add_component_to_blueprint(bp,DirectionalLightComponent, "Directional_light")

# add node variables (get) to the graph
    intensity_node = bp.UberGraphPages[0].graph_add_node_variable_get('intensity', None, 200, 100)
    directional_light_node = bp.UberGraphPages[0].graph_add_node_variable_get('Directional_light', None, 200, 0)

# add the SetIntensity node (from DirectionalLightComponent)
    directional_light_set_intensity = bp.UberGraphPages[0].graph_add_node_call_function(DirectionalLightComponent.SetIntensity, 400, 0)

# link variables
    intensity_node.node_find_pin('intensity').make_link_to(directional_light_set_intensity.node_find_pin('NewIntensity'))
    directional_light_node.node_find_pin('Directional_light').make_link_to(directional_light_set_intensity.node_find_pin('self'))

# a commodity function for finding an event node
    def get_event_node(event_name):
        for node in bp.UberGraphPages[0].Nodes:
            if node.is_a(K2Node_Event):
                if node.EventReference.MemberName == event_name:
                    return node

# get the ReceiveBeginPlay event node
    begin_play_node = get_event_node('ReceiveBeginPlay')

# link BeginPlay to SetIntensity
    begin_play_node.node_find_pin('then').make_link_to(directional_light_set_intensity.node_find_pin('execute'))

# compile the blueprint
    ue.compile_blueprint(bp)

# open related editor
    ue.open_editor_for_asset(bp)

# spawn it
    ue.get_editor_world().actor_spawn(bp.GeneratedClass)

