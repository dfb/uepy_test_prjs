'''
testing output parameters:
+ py calls bp
+ py calls py via engine (not direct)
+ py calls C++
+ C++ calls py
+ BP calls py
- next:
    - Py calling Py via ufunction that implements interface
    - BP calling Py via ufunction that implements interface

Tests various combinations of numbers of input params, output params, and whether or not the base class method has a return value
(in BP, there is no return param - just out params - but in C++ you can have either or both)
'''

from helpers import *
from unreal_engine.classes import BlueprintGeneratedClass, Blueprint, Class, Class, Actor, TestRecorder, StrProperty
import difflib
ue.allow_actor_script_execution_in_editor(True)

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

CTester = ue.load_object(Class, '/Script/output_params.Tester')
BTester = ue.load_object(Blueprint, '/Game/BTester.BTester').GeneratedClass

# the original actor names no longer make sense, so map them all to something easier to use
CTestActor = ue.load_object(Class, '/Script/output_params.TestActor')
BTestActor = ue.load_object(Blueprint, '/Game/BTestActor.BTestActor').GeneratedClass

def sargs(args):
    '''stringifies args in a consistent and easily comparable way'''
    if args is None:
        ret = 'None'
    elif type(args) is int:
        ret = str(args)
    elif type(args) is float:
        ret = '%.3f' % args
    elif type(args) is str:
        ret = args
    else:
        ret = []
        for x in args:
            if type(x) is float:
                x = '%.3f' % x
            else:
                x = str(x)
            ret.append(x)
        ret = ','.join(ret)
    return ret

def PCall(caller, callee, method, *args):
    '''helper for Python calling BP or Py'''
    tr.Note(caller, 'send', sargs(args))
    ret = getattr(callee, method)(*args)
    tr.Note(caller, 'recv', sargs(ret))

class PTestActor(CTestActor):
    # 0 output params
    def M000(self):
        tr.Note('M000', 'recv')

    def M100(self, i:int):
        tr.Note('M100', 'recv', sargs((i,)))

    def M200(self, i:int, f:float):
        tr.Note('M200', 'recv', sargs((i, f)))

    def M001(self) -> float:
        tr.Note('M001', 'recv')
        return 99.5

    def M101(self, i:int) -> float:
        tr.Note('M101', 'recv', sargs((i,)))
        return i/2.0

    def M201(self, i:int, f:float) -> float:
        tr.Note('M201', 'recv', sargs((i,f)))
        return i * f

    def M010(self) -> int:
        tr.Note('M010', 'recv')
        return 71

    def M110(self, i:int) -> int:
        tr.Note('M110', 'recv', sargs((i,)))
        return i*2

    def M210(self, i:int, f:float) -> int:
        tr.Note('M210', 'recv', sargs((i, f)))
        return int(i * f)

    def M011(self) -> (int, float):
        tr.Note('M011', 'recv')
        return 15, 4.321

    def M111(self, i:int) -> (int, float):
        tr.Note('M111', 'recv', sargs((i,)))
        return i//2, i/2

    def M211(self, i:int, f:float) -> (int, float):
        tr.Note('M211', 'recv', sargs((i,f)))
        return i//int(f), i/f

    def M020(self) -> (int, float):
        tr.Note('M020', 'recv')
        return 11, 9.111

    def M120(self, i:int) -> (int, float):
        tr.Note('M120', 'recv', sargs((i,)))
        return i*2, i*3.5

    def M220(self, i:int, f:float) -> (int, float):
        tr.Note('M220', 'recv', sargs((i,f)))
        return i+int(f), i+f

    def M021(self) -> (int, float, float):
        tr.Note('M021', 'recv')
        return 99, 98.765, 4.321

    def M121(self, i:int) -> (int, float, float):
        tr.Note('M121', 'recv', sargs((i,)))
        return i*2, i/10.0, i/7.0

    def M221(self, i:int, f:float) -> (int, float, float):
        tr.Note('M221', 'recv', sargs((i,f)))
        return i*3, f*2.0, i*3*f*2.0

EXPECTED = '''
tester|send|
M000|recv|
tester|recv|None

tester|send|55
M100|recv|55
tester|recv|None

tester|send|17,2.500
M200|recv|17,2.500
tester|recv|None

tester|send|
M001|recv|
tester|recv|99.500

tester|send|13
M101|recv|13
tester|recv|6.500

tester|send|2,7.500
M201|recv|2,7.500
tester|recv|15.000

tester|send|
M010|recv|
tester|recv|71

tester|send|80
M110|recv|80
tester|recv|160

tester|send|20,2.500
M210|recv|20,2.500
tester|recv|50

tester|send|
M011|recv|
tester|recv|15,4.321

tester|send|53
M111|recv|53
tester|recv|26,26.500

tester|send|17,3.500
M211|recv|17,3.500
tester|recv|5,4.857

tester|send|
M020|recv|
tester|recv|11,9.111

tester|send|7
M120|recv|7
tester|recv|14,24.500

tester|send|9,3.577
M220|recv|9,3.577
tester|recv|12,12.577

tester|send|
M021|recv|
tester|recv|99,98.765,4.321

tester|send|43
M121|recv|43
tester|recv|86,4.300,6.143

tester|send|7,8.215
M221|recv|7,8.215
tester|recv|21,16.430,345.030
'''

class PTester(CTester):
    def RunTests(self, rec:TestRecorder, callee:CTestActor):
        # No out params
        PCall('tester', callee, 'M000')
        PCall('tester', callee, 'M100', 55)
        PCall('tester', callee, 'M200', 17, 2.5)
        PCall('tester', callee, 'M001')
        PCall('tester', callee, 'M101', 13)
        PCall('tester', callee, 'M201', 2, 7.5)

        # 1 out param
        PCall('tester', callee, 'M010')
        PCall('tester', callee, 'M110', 80)
        PCall('tester', callee, 'M210', 20, 2.5)
        PCall('tester', callee, 'M011')
        PCall('tester', callee, 'M111', 53)
        PCall('tester', callee, 'M211', 17, 3.5)

        # 2 out params
        PCall('tester', callee, 'M020')
        PCall('tester', callee, 'M120', 7)
        PCall('tester', callee, 'M220', 9, 3.577)
        PCall('tester', callee, 'M021')
        PCall('tester', callee, 'M121', 43)
        PCall('tester', callee, 'M221', 7, 8.215)

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

