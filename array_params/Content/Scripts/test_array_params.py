'''
testing array parameters

for each combination of one language calling another:
    for each: int, bool, fvector, string, object, scriptstruct:
         test array in
         test array out
         test array ret
         test array in, out, ret

NEXT:
- impl bool tests
- impl rest of tests
- review code, submit patch
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
    if type(arg) is bool: return str(int(arg))
    if type(arg) is FVector: return 'Vec(%.3f,%.3f,%.3f)' % (arg.x, arg.y, arg.z)
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

        PCall('tester', callee, 'BoolIn', 44, [True, False, False, True, True], 202.511)
        PCall('tester', callee, 'BoolOut', 81)
        PCall('tester', callee, 'BoolRet', 6991)
        PCall('tester', callee, 'BoolInOutRet', 32711, [False, False, True, False, False, True, False, True, True, True])

        PCall('tester', callee, 'VectorIn', 3819, [FVector(1,2,3), FVector(4,5,6)], 117.880)
        PCall('tester', callee, 'VectorOut', 7777)
        PCall('tester', callee, 'VectorRet', 5110)
        PCall('tester', callee, 'VectorInOutret', 99411, [FVector(10,11,12),FVector(13,14,15),FVector(16,17,18),FVector(19,20,-21)])

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

    def BoolIn(self, i:int, bools:[bool], f:float):
        tr.Note('BoolIn', 'recv', sargs(i, bools, f))

    def BoolOut(self, i:int) -> ([bool], float):
        tr.Note('BoolOut', 'recv', sargs(i))
        ret = [False, True, False, False, True], 55.125
        tr.Note('BoolOut', 'send', sretargs(ret))
        return ret

    def BoolRet(self, i:int) -> [bool]:
        tr.Note('BoolRet', 'recv', sargs(i))
        ret = [True, False, True, False, False, True, True];
        tr.Note('BoolRet', 'send', sretargs(ret))
        return ret

    def BoolInOutRet(self, i:int, inBools:[bool]) -> ([bool], float, [bool]):
        tr.Note('BoolInOutRet', 'recv', sargs(i, inBools))
        ret = [True, False, False, True, True, True, True, True, False], 1125.865, [True, True, False, False, False, True, False, False, True, True]
        tr.Note('BoolInOutRet', 'send', sretargs(ret))
        return ret

    def VectorIn(self, i:int, vectors:[FVector], f:float):
        tr.Note('VectorIn', 'recv', sargs(i, vectors, f))
        tr.Note('VectorIn', 'send', 'None')

    def VectorOut(self, i:int) -> ([FVector], float):
        tr.Note('VectorOut', 'recv', sargs(i))
        ret = [FVector(5.5, 4.5, 3.5),FVector(-1.2, -10, 5000),FVector(17.125, -105.177, 32.111)], 99.101
        tr.Note('VectorOut', 'send', sretargs(ret))
        return ret

    def VectorRet(self, i:int) -> [FVector]:
        tr.Note('VectorRet', 'recv', sargs(i))
        ret = [FVector(11.225,-5.0,33.333), FVector(5,4,3), FVector(-1,-10,-100)]
        tr.Note('VectorRet', 'send', sretargs(ret))
        return ret

    def VectorInOutRet(self, i:int, inVectors:[FVector]) -> ([FVector], float, [FVector]):
        tr.Note('VectorInOutRet', 'recv', sargs(i, inVectors))
        ret = [True, False, False, True, True, True, True, True, False], 1125.865, [True, True, False, False, False, True, False, False, True, True]
        ret = [FVector(1.111,2.222,3.333), FVector(4.444,5.555,6.666)], 1151.966, \
                [FVector(100.000,200.000,300.000), FVector(400.000,500.000,600.000), FVector(10.000,20.000,30.000), FVector(40.000,50.000,60.000)]
        tr.Note('VectorInOutRet', 'send', sretargs(ret))
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


tester|send|44,[1,0,0,1,1],202.511
BoolIn|recv|44,[1,0,0,1,1],202.511
tester|recv|None

tester|send|81
BoolOut|recv|81
BoolOut|send|[0,1,0,0,1],55.125
tester|recv|[0,1,0,0,1],55.125

tester|send|6991
BoolRet|recv|6991
BoolRet|send|[1,0,1,0,0,1,1]
tester|recv|[1,0,1,0,0,1,1]

tester|send|32711,[0,0,1,0,0,1,0,1,1,1]
BoolInOutRet|recv|32711,[0,0,1,0,0,1,0,1,1,1]
BoolInOutRet|send|[1,0,0,1,1,1,1,1,0],1125.865,[1,1,0,0,0,1,0,0,1,1]
tester|recv|[1,0,0,1,1,1,1,1,0],1125.865,[1,1,0,0,0,1,0,0,1,1]


tester|send|3819,[Vec(1.000,2.000,3.000),Vec(4.000,5.000,6.000)],117.880
VectorIn|recv|3819,[Vec(1.000,2.000,3.000),Vec(4.000,5.000,6.000)],117.880
VectorIn|send|None
tester|recv|None

tester|send|7777
VectorOut|recv|7777
VectorOut|send|[Vec(5.500,4.500,3.500),Vec(-1.200,-10.000,5000.000),Vec(17.125,-105.177,32.111)],99.101
tester|recv|[Vec(5.500,4.500,3.500),Vec(-1.200,-10.000,5000.000),Vec(17.125,-105.177,32.111)],99.101

tester|send|5110
VectorRet|recv|5110
VectorRet|send|[Vec(11.225,-5.000,33.333),Vec(5.000,4.000,3.000),Vec(-1.000,-10.000,-100.000)]
tester|recv|[Vec(11.225,-5.000,33.333),Vec(5.000,4.000,3.000),Vec(-1.000,-10.000,-100.000)]

tester|send|99411,[Vec(10.000,11.000,12.000),Vec(13.000,14.000,15.000),Vec(16.000,17.000,18.000),Vec(19.000,20.000,-21.000)]
VectorInOutRet|recv|99411,[Vec(10.000,11.000,12.000),Vec(13.000,14.000,15.000),Vec(16.000,17.000,18.000),Vec(19.000,20.000,-21.000)]
VectorInOutRet|send|[Vec(1.111,2.222,3.333),Vec(4.444,5.555,6.666)],1151.966,[Vec(100.000,200.000,300.000),Vec(400.000,500.000,600.000),Vec(10.000,20.000,30.000),Vec(40.000,50.000,60.000)]
tester|recv|[Vec(1.111,2.222,3.333),Vec(4.444,5.555,6.666)],1151.966,[Vec(100.000,200.000,300.000),Vec(400.000,500.000,600.000),Vec(10.000,20.000,30.000),Vec(40.000,50.000,60.000)]

'''

def Debug(title, testerClass, actorClass):
    tester = Spawn(testerClass, nuke=True)
    actor = Spawn(actorClass, nuke=True)
    try:
        log('===== DEBUG START %s =====' % title)
        tr.Clear()
        actor.SetRecorder(tr)
        tester.RunDebugTest(tr, actor)
        log(tr.GetLines())
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

#Debug('BP calling Py', BTester, PTestActor)

if 1:
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

