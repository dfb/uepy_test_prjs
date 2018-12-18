import sys, os
import unreal_engine as ue
from unreal_engine import UObject, FVector, FRotator, FTransform, FColor, FLinearColor
from unreal_engine.classes import Pawn
import traceback

def log(*args):
    print(' '.join(str(x) for x in args))

def logTB():
    for line in traceback.format_exc().split('\n'):
        log(line)

try:
    from unreal_engine.enums import EWorldType
except ImportError:
    # Not implemented yet - for some reason EWorldType isn't a UENUM so the automagic importer can't work
    class EWorldType:
        NONE, Game, Editor, PIE, EditorPreview, GamePreview, Inactive = range(7)

def GetWorld():
    '''Returns the best guess of what the "current" world to use is'''
    worlds = {} # worldType -> *first* world of that type
    for w in ue.all_worlds():
        t = w.get_world_type()
        if worlds.get(t) is None:
            worlds[t] = w

    return worlds.get(EWorldType.Game) or worlds.get(EWorldType.PIE) or worlds.get(EWorldType.Editor)

def Spawn(cls, world=None, select=False, nuke=False):
    '''General purpose spawn function - spawns an actor and returns it. If no world is provided, finds one
    using GetWorld. cls can be:
    - the name of the class as a string, in which case it will be imported from unreal_engine.classes
    - a class previously imported from unreal_engine.classes
    - a Python class created via the fm.subclassing module
    If the current world is the editor world and select=True, then the newly spawned actor will be
    selected before returning.
    '''
    world = world or GetWorld()
    if isinstance(cls, str):
        import unreal_engine.classes as c
        cls = getattr(c, cls)

    if nuke:
        for obj in ue.get_editor_world().all_objects()[:]:
            try:
                if obj.is_a(cls) and obj.is_valid():
                    obj.actor_destroy()
            except:
                pass #logTB() # TODO: grr, there is some mystery object that is in an invalid state that logs an error - it'd be nice to find it and handle it better

    if select:
        ue.editor_deselect_actors()

    try:
        ue.allow_actor_script_execution_in_editor(True)
        newObj = world.actor_spawn(cls)
    finally:
        ue.allow_actor_script_execution_in_editor(False)

    if select:
        ue.editor_select_actor(newObj)

    return newObj

