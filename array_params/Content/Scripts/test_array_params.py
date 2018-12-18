'''
testing array parameters

for each combination of one language calling another:
    for each: int, bool, fvector string, object, scriptstruct:
         test array in
         test array out
         test array ret
         test array in, out, ret
'''

from helpers import *
from unreal_engine.classes import BlueprintGeneratedClass, Blueprint, Class, Class, Actor, TestRecorder, StrProperty
import difflib
from typing import List
ue.allow_actor_script_execution_in_editor(True)

def sarg(arg):
    if arg is None: return 'None'
    if type(arg) is int: return str(arg)
    if type(arg) is float: return '%.3f' % arg
    if type(arg) is str: return arg
    if type(arg) is list: return '[%s]' % (','.join(sarg(x) for x in arg))
    if type(arg) is tuple: return sargs(arg)
    assert 0, repr(arg)

def sargs(*args):
    '''stringifies args in a consistent and easily comparable way'''
    ret = [sarg(arg) for arg in args]
    return ','.join(ret)

def sretargs(ret):
    if type(ret) is tuple:
        return sargs(*ret)
    return sarg(ret)

class PTestRecorder(TestRecorder):
    '''records inputs and outputs of tests of calls between BP and Python'''
    def End(self, expected:str):
        cur = [x for x in [x.strip() for x in self.GetLines().split('\n')] if x]
        exp = [x for x in [x.strip() for x in expected.split('\n')] if x]
        if cur == exp:
            log('**** PASSED:', self.GetCurTestName())
        else:
            diff = difflib.context_diff(exp, cur, fromfile='expected', tofile='current')
            diff = '\n'.join(diff)
            log(diff)
            log('**** FAILED:', self.GetCurTestName())

tr = Spawn(PTestRecorder, nuke=True)

def PCall(caller, callee, method, *args):
    '''helper for Python calling BP or Py'''
    tr.Note(caller, 'send', sargs(*args))
    ret = getattr(callee, method)(*args)
    tr.Note(caller, 'recv', sretargs(ret))

CTester = ue.load_object(Class, '/Script/array_params.Tester')
BTester = ue.load_object(Blueprint, '/Game/BTester.BTester').GeneratedClass
CTestActor = ue.load_object(Class, '/Script/array_params.TestActor')
BTestActor = ue.load_object(Blueprint, '/Game/BTestActor.BTestActor').GeneratedClass

class PTester(CTester):
    def RunTests(self, rec:TestRecorder, callee:CTestActor):
        PCall('tester', callee, 'IntIn', 10, [55, 57, 59, 61], 3.5)
        PCall('tester', callee, 'IntOut', 13)
        PCall('tester', callee, 'IntRet', 45)
        PCall('tester', callee, 'IntInOutRet', 51, [99,89,79,69,59,49,39,29,19,9,-1])

class PTestActor(CTestActor):
    def IntIn(self, i:int, ints:[int], f:float):
        tr.Note('IntIn', 'recv', sargs(i, ints, f))

    def IntOut(self, i:int) -> ([int], float):
        tr.Note('IntOut', 'recv', sargs(i))
        ret = [32, -16, 5], 1234.0
        tr.Note('IntOut', 'send', sretargs(ret))
        return ret

    def IntRet(self, i:int)-> [int]:
        tr.Note('IntRet', 'recv', sargs(i))
        ret = [101, 55, -4]
        tr.Note('IntRet', 'send', sargs(ret))
        return ret

    def IntInOutRet(self, i:int, inInts:[int]) -> ([int], float, [int]):
        tr.Note('IntInOutRet', 'recv', sargs(i, inInts))
        ret = [-11, 37, 1011, 65535], 113.117, [16,32,64,128,256,512]
        tr.Note('IntInOutRet', 'send', sretargs(ret))
        return ret

EXPECTED = '''
tester|send|10,[55,57,59,61],3.500
IntIn|recv|10,[55,57,59,61],3.500
tester|recv|None

tester|send|13
IntOut|recv|13
IntOut|send|[32,-16,5],1234.000
tester|recv|[32,-16,5],1234.000

tester|send|45
IntRet|recv|45
IntRet|send|[101,55,-4]
tester|recv|[101,55,-4]

tester|send|51,[99,89,79,69,59,49,39,29,19,9,-1]
IntInOutRet|recv|51,[99,89,79,69,59,49,39,29,19,9,-1]
IntInOutRet|send|[-11,37,1011,65535],113.117,[16,32,64,128,256,512]
tester|recv|[-11,37,1011,65535],113.117,[16,32,64,128,256,512]

'''

def Debug(title, testerClass, actorClass):
    tester = Spawn(testerClass, nuke=True)
    actor = Spawn(actorClass, nuke=True)
    try:
        log('===== DEBUG START %s =====' % title)
        actor.SetRecorder(tr)
        tester.RunDebugTest(tr, actor)
        tr.Clear()
    finally:
        actor.DestroyActor()
        tester.DestroyActor()

def Run(title, testerClass, actorClass):
    tester = Spawn(testerClass, nuke=True)
    actor = Spawn(actorClass, nuke=True)
    try:
        tr.Clear()
        tr.Begin(title)
        actor.SetRecorder(tr)
        tester.RunTests(tr, actor)
        tr.End(EXPECTED)
        tr.Clear()
    finally:
        actor.DestroyActor()
        tester.DestroyActor()

Run('C++ calling C++', CTester, CTestActor)
Run('C++ calling BP', CTester, BTestActor)
Run('C++ calling Py', CTester, PTestActor)
Run('Py calling C++', PTester, CTestActor)
Run('Py calling BP', PTester, BTestActor)
Run('Py calling Py', PTester, PTestActor)
Run('BP calling C++', BTester, CTestActor)
Run('BP calling BP', BTester, BTestActor)
Run('BP calling Py', BTester, PTestActor)

tr.DestroyActor()
ue.allow_actor_script_execution_in_editor(False)
