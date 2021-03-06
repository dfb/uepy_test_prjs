#include "TestClasses.h"

DECLARE_LOG_CATEGORY_EXTERN(ARRAY_PARAMS, Log, All);

#define LOG(format, ...) UE_LOG(ARRAY_PARAMS, Log, TEXT("[%s:%d] %s"), TEXT(__FUNCTION__), __LINE__, *FString::Printf(TEXT(format), ##__VA_ARGS__ ))

DEFINE_LOG_CATEGORY(ARRAY_PARAMS);

// TODO: now that we have a pattern, templatize this mess

void ATestRecorder::Note(FString who, FString action, FString args)
{
    FString line = FString::Printf(_T("%s|%s|%s"), *who, *action, *args);
    lines.Emplace(line);
    //LOG("%s", *line);
}

AParamActor *AParamActor::SpawnWithName(UObject *WorldContextObject, FString withName)
{
    FVector loc;
    UWorld* world = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull);
    FActorSpawnParameters spawnParams;
	spawnParams.bNoFail = true;
    spawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AParamActor *actor = (AParamActor*)world->SpawnActor(AParamActor::StaticClass(), &loc, nullptr, spawnParams);
    actor->SetTestName(withName);
    return actor;
}

void AParamActor::DestroyActors(UObject *WorldContextObject, const TArray<AParamActor*>& actors)
{
    UWorld* world = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull);
    for (auto actor : actors)
        world->DestroyActor(actor);
}

FString Str(const FTestStruct& s)
{
    return FString::Printf(_T("TS(%s,%d)"), *s.name, s.number);
}

FString Str(const TArray<FTestStruct>& params)
{
    TArray<FString> parts;
    for (auto& p : params)
        parts.Emplace(Str(p));
    return FString::Printf(_T("[%s]"), *FString::Join(parts, _T(",")));
}

FString Str(const AParamActor *a)
{
    FString name = a->GetTestName();
    return FString::Printf(_T("Actor(%s)"), *name);
}

FString Str(const TArray<AParamActor*>& params)
{
    TArray<FString> parts;
    for (auto& p : params)
        parts.Emplace(Str(p));
    return FString::Printf(_T("[%s]"), *FString::Join(parts, _T(",")));
}

FString Str(const FString s)
{
    return FString::Printf(_T("\"%s\""), *s);
}

FString Str(const TArray<FString>& params)
{
    TArray<FString> parts;
    for (auto& p : params)
        parts.Emplace(Str(p));
    return FString::Printf(_T("[%s]"), *FString::Join(parts, _T(",")));
}

FString Str(const FVector& v)
{
    return FString::Printf(_T("Vec(%.3f,%.3f,%.3f)"), v.X, v.Y, v.Z);
}

FString Str(const TArray<FVector>& params)
{
    TArray<FString> parts;
    for (auto& p : params)
        parts.Emplace(Str(p));
    return FString::Printf(_T("[%s]"), *FString::Join(parts, _T(",")));
}

FString Str(const TArray<int32>& array)
{
    TArray<FString> parts;
    for (int32 a : array)
        parts.Emplace(FString::Printf(_T("%d"), a));
    return FString::Printf(_T("[%s]"), *FString::Join(parts, _T(",")));
}

FString Str(const TArray<bool>& array)
{
    TArray<FString> parts;
    for (bool a : array)
        parts.Emplace(FString::Printf(_T("%d"), a));
    return FString::Printf(_T("[%s]"), *FString::Join(parts, _T(",")));
}

void ATestActor::IntIn_Implementation(int i, const TArray<int32>& ints, float f)
{
    FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(ints), f);
    recorder->Note(_T("IntIn"), _T("recv"), *args);
}

void ATestActor::IntOut_Implementation(int i, TArray<int32>& ints, float& of)
{
    ints.Empty();
    ints.Emplace(32);
    ints.Emplace(-16);
    ints.Emplace(5);
    of = 1234;
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("IntOut"), _T("recv"), *args);
    args = FString::Printf(_T("%s,%.3f"), *Str(ints), of);
    recorder->Note(_T("IntOut"), _T("send"), *args);
}

TArray<int32> ATestActor::IntRet_Implementation(int i)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("IntRet"), _T("recv"), *args);
    TArray<int32> ints = {101, 55, -4};
    args = Str(ints);
    recorder->Note(_T("IntRet"), _T("send"), *args);
    return ints;
}

TArray<int32> ATestActor::IntInOutRet_Implementation(int i, const TArray<int32>& inInts, TArray<int32>& outInts, float& of)
{
    FString args = FString::Printf(_T("%d,%s"), i, *Str(inInts));
    recorder->Note(_T("IntInOutRet"), _T("recv"), *args);
    of = 113.117;
    outInts.Empty();
    outInts.Emplace(-11);
    outInts.Emplace(37);
    outInts.Emplace(1011);
    outInts.Emplace(65535);
    TArray<int32> retInts = {16, 32, 64, 128, 256, 512};
    args = FString::Printf(_T("%s,%.3f,%s"), *Str(outInts), of, *Str(retInts));
    recorder->Note(_T("IntInOutRet"), _T("send"), *args);
    return retInts;
}

void ATestActor::BoolIn_Implementation(int i, const TArray<bool>& bools, float f)
{
    FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(bools), f);
    recorder->Note(_T("BoolIn"), _T("recv"), *args);
}

void ATestActor::BoolOut_Implementation(int i, TArray<bool>& bools, float& of)
{
    bools.Empty();
    bools.Emplace(false);
    bools.Emplace(true);
    bools.Emplace(false);
    bools.Emplace(false);
    bools.Emplace(true);
    of = 55.125;
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("BoolOut"), _T("recv"), *args);
    args = FString::Printf(_T("%s,%.3f"), *Str(bools), of);
    recorder->Note(_T("BoolOut"), _T("send"), *args);
}

TArray<bool> ATestActor::BoolRet_Implementation(int i)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("BoolRet"), _T("recv"), *args);
    TArray<bool> ret = {true, false, true, false, false, true, true};
    recorder->Note(_T("BoolRet"), _T("send"), *Str(ret));
    return ret;
}

TArray<bool> ATestActor::BoolInOutRet_Implementation(int i, const TArray<bool>& inBools, TArray<bool>& outBools, float& of)
{
    FString args = FString::Printf(_T("%d,%s"), i, *Str(inBools));
    recorder->Note(_T("BoolInOutRet"), _T("recv"), *args);
    of = 1125.865;
    outBools.Empty();
    outBools.Emplace(true);
    outBools.Emplace(false);
    outBools.Emplace(false);
    outBools.Emplace(true);
    outBools.Emplace(true);
    outBools.Emplace(true);
    outBools.Emplace(true);
    outBools.Emplace(true);
    outBools.Emplace(false);
    TArray<bool> ret = {true, true, false, false, false, true, false, false, true, true};
    args = FString::Printf(_T("%s,%.3f,%s"), *Str(outBools), of, *Str(ret));
    recorder->Note(_T("BoolInOutRet"), _T("send"), *args);
    return ret;
}

void ATestActor::VectorIn_Implementation(int i, const TArray<FVector>& inputs, float f)
{
    FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inputs), f);
    recorder->Note(_T("VectorIn"), _T("recv"), *args);
    recorder->Note(_T("VectorIn"), _T("send"), _T("None"));
}

void ATestActor::VectorOut_Implementation(int i, TArray<FVector>& outputs, float& of)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("VectorOut"), _T("recv"), *args);
    outputs.Empty();
    outputs.Emplace(FVector(5.5, 4.5, 3.5));
    outputs.Emplace(FVector(-1.2, -10, 5000));
    outputs.Emplace(FVector(17.125, -105.177, 32.111));
    of = 99.101;
    args = FString::Printf(_T("%s,%.3f"), *Str(outputs), of);
    recorder->Note(_T("VectorOut"), _T("send"), *args);
}

TArray<FVector> ATestActor::VectorRet_Implementation(int i)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("VectorRet"), _T("recv"), *args);
    TArray<FVector> ret = {FVector(11.225,-5.0,33.333), FVector(5,4,3), FVector(-1,-10,-100)};
    recorder->Note(_T("VectorRet"), _T("send"), *Str(ret));
    return ret;
}

TArray<FVector> ATestActor::VectorInOutRet_Implementation(int i, const TArray<FVector>& inParam, TArray<FVector>& outParam, float& of)
{
    FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
    recorder->Note(_T("VectorInOutRet"), _T("recv"), *args);
    of = 1151.966;
    outParam.Empty();
    outParam.Emplace(FVector(1.111, 2.222, 3.333));
    outParam.Emplace(FVector(4.444,5.555,6.666));
    TArray<FVector> ret = {FVector(100,200,300), FVector(400,500,600),FVector(10,20,30),FVector(40,50,60)};
    args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(ret));
    recorder->Note(_T("VectorInOutRet"), _T("send"), *args);
    return ret;
}

void ATestActor::StringIn_Implementation(int i, const TArray<FString>& inputs, float f)
{
    FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inputs), f);
    recorder->Note(_T("StringIn"), _T("recv"), *args);
    recorder->Note(_T("StringIn"), _T("send"), _T("None"));
}

void ATestActor::StringOut_Implementation(int i, TArray<FString>& outputs, float& of)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("StringOut"), _T("recv"), *args);
    outputs.Empty();
    outputs.Emplace(_T("Jan"));
    outputs.Emplace(_T("February"));
    outputs.Emplace(_T("MaRzO"));
    of = -113.311;
    args = FString::Printf(_T("%s,%.3f"), *Str(outputs), of);
    recorder->Note(_T("StringOut"), _T("send"), *args);
}

TArray<FString> ATestActor::StringRet_Implementation(int i)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("StringRet"), _T("recv"), *args);
    TArray<FString> ret = {_T("Enero"), _T("Febrero"), _T("Marzo"), _T("Abril")};
    recorder->Note(_T("StringRet"), _T("send"), *Str(ret));
    return ret;
}

TArray<FString> ATestActor::StringInOutRet_Implementation(int i, const TArray<FString>& inParam, TArray<FString>& outParam, float& of)
{
    FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
    recorder->Note(_T("StringInOutRet"), _T("recv"), *args);
    of = 77.115;
    outParam.Empty();
    outParam.Emplace(_T("Origin"));
    outParam.Emplace(_T("Rebates"));
    outParam.Emplace(_T("Foreseen"));
    outParam.Emplace(_T("Abner"));
    TArray<FString> ret = {_T("Battery"),_T("Mouse"),_T("Pad"),_T("Charger"),_T("Cord")};
    args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(ret));
    recorder->Note(_T("StringInOutRet"), _T("send"), *args);
    return ret;
}

void ATestActor::ActorIn_Implementation(int i, const TArray<AParamActor*>& inputs, float f)
{
    FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inputs), f);
    recorder->Note(_T("ActorIn"), _T("recv"), *args);
    recorder->Note(_T("ActorIn"), _T("send"), _T("None"));
}

void ATestActor::ActorOut_Implementation(int i, TArray<AParamActor*>& outputs, float& of)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("ActorOut"), _T("recv"), *args);
    outputs.Empty();
    outputs.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Joseph")));
    outputs.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Hyrum")));
    outputs.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Alvin")));
    of = 254.061;
    args = FString::Printf(_T("%s,%.3f"), *Str(outputs), of);
    recorder->Note(_T("ActorOut"), _T("send"), *args);
}

TArray<AParamActor*> ATestActor::ActorRet_Implementation(int i)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("ActorRet"), _T("recv"), *args);
    TArray<AParamActor*> ret;
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Luke")));
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Han")));
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Leia")));
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Lando")));
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Bobba")));
    recorder->Note(_T("ActorRet"), _T("send"), *Str(ret));
    return ret;
}

TArray<AParamActor*> ATestActor::ActorInOutRet_Implementation(int i, const TArray<AParamActor*>& inParam, TArray<AParamActor*>& outParam, float& of)
{
    FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
    recorder->Note(_T("ActorInOutRet"), _T("recv"), *args);
    of = 98.715;
    outParam.Empty();
    outParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Up")));
    outParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Down")));
    outParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Left")));
    outParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Right")));
    TArray<AParamActor*> ret;
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("North")));
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("South")));
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("East")));
    ret.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("wEsT")));
    args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(ret));
    recorder->Note(_T("ActorInOutRet"), _T("send"), *args);
    return ret;
}

void ATestActor::StructIn_Implementation(int i, const TArray<FTestStruct>& inputs, float f)
{
    FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inputs), f);
    recorder->Note(_T("StructIn"), _T("recv"), *args);
    recorder->Note(_T("StructIn"), _T("send"), _T("None"));
}

void ATestActor::StructOut_Implementation(int i, TArray<FTestStruct>& outputs, float& of)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("StructOut"), _T("recv"), *args);
    outputs.Empty();
    TArray<FTestStruct> inParam;
    FTestStruct ts;
    ts.name = _T("Monday"); ts.number = 5; outputs.Emplace(ts);
    ts.name = _T("toozdee"); ts.number = 10; outputs.Emplace(ts);
    ts.name = _T("Wed"); ts.number = 15; outputs.Emplace(ts);
    ts.name = _T("Thirsty"); ts.number = 20; outputs.Emplace(ts);
    of = 9.895;
    args = FString::Printf(_T("%s,%.3f"), *Str(outputs), of);
    recorder->Note(_T("StructOut"), _T("send"), *args);
}

TArray<FTestStruct> ATestActor::StructRet_Implementation(int i)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("StructRet"), _T("recv"), *args);
    TArray<FTestStruct> ret;
    FTestStruct ts;
    ts.name = _T("Red"); ts.number = 101; ret.Emplace(ts);
    ts.name = _T("Blue"); ts.number = 102; ret.Emplace(ts);
    ts.name = _T("Green"); ts.number = 103; ret.Emplace(ts);
    ts.name = _T("Orange"); ts.number = 104; ret.Emplace(ts);
    recorder->Note(_T("StructRet"), _T("send"), *Str(ret));
    return ret;
}

TArray<FTestStruct> ATestActor::StructInOutRet_Implementation(int i, const TArray<FTestStruct>& inParam, TArray<FTestStruct>& outParam, float& of)
{
    FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
    recorder->Note(_T("StructInOutRet"), _T("recv"), *args);
    of = 101.125;
    outParam.Empty();
    FTestStruct ts;
    ts.name = _T("Spring"); ts.number = 5001; outParam.Emplace(ts);
    ts.name = _T("Summer"); ts.number = -5002; outParam.Emplace(ts);
    ts.name = _T("Fall"); ts.number = 5003; outParam.Emplace(ts);
    ts.name = _T("Winter"); ts.number = -5004; outParam.Emplace(ts);
    TArray<FTestStruct> ret;
    ts.name = _T("Brighton"); ts.number = 16; ret.Emplace(ts);
    ts.name = _T("Alta"); ts.number = 18; ret.Emplace(ts);
    ts.name = _T("Solitude"); ts.number = 20; ret.Emplace(ts);
    args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(ret));
    recorder->Note(_T("StructInOutRet"), _T("send"), *args);
    return ret;
}


void ATester::RunDebugTest(ATestRecorder *recorder, ATestActor *callee)
{
    LOG("WTH??");
}

void ATester::RunTests(ATestRecorder *recorder, ATestActor *callee)
{
    // bool
    {
        TArray<int32> ints = {55, 57, 59, 61};
        int i = 10;
        float f = 3.5;
        FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(ints), f);
        recorder->Note(_T("tester"), _T("send"), *args);
        callee->IntIn(i, ints, f);
        recorder->Note(_T("tester"), _T("recv"), _T("None"));
    }
    {
        TArray<int32> ints;
        float f;
        recorder->Note(_T("tester"), _T("send"), _T("13"));
        callee->IntOut(13, ints, f);
        FString args = FString::Printf(_T("%s,%.3f"), *Str(ints), f);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        recorder->Note(_T("tester"), _T("send"), _T("45"));
        TArray<int32> ints = callee->IntRet(45);
        FString args = Str(ints);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 51;
        TArray<int32> inInts = {99, 89, 79, 69, 59, 49, 39, 29, 19, 9, -1};
        FString args = FString::Printf(_T("%d,%s"), i, *Str(inInts));
        recorder->Note(_T("tester"), _T("send"), args);
        float of = 0.0f;
        TArray<int32> retInts, outInts;
        retInts = callee->IntInOutRet(i, inInts, outInts, of);
        args = FString::Printf(_T("%s,%.3f,%s"), *Str(outInts), of, *Str(retInts));
        recorder->Note(_T("tester"), _T("recv"), args);
    }

    // bool
    {
        int i = 44;
        TArray<bool> bools = {true, false, false, true, true};
        float f = 202.511;
        FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(bools), f);
        recorder->Note(_T("tester"), _T("send"), *args);
        callee->BoolIn(i, bools, f);
        recorder->Note(_T("tester"), _T("recv"), _T("None"));
    }
    {
        TArray<bool> bools;
        float f;
        recorder->Note(_T("tester"), _T("send"), _T("81"));
        callee->BoolOut(81, bools, f);
        FString args = FString::Printf(_T("%s,%.3f"), *Str(bools), f);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 6991;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        TArray<bool> bools = callee->BoolRet(i);
        args = FString::Printf(_T("%s"), *Str(bools));
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 32711;
        TArray<bool> inParam = {false, false, true, false, false, true, false, true, true, true};
        FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
        recorder->Note(_T("tester"), _T("send"), args);
        float of = 0.0f;
        TArray<bool> retParam, outParam;
        retParam = callee->BoolInOutRet(i, inParam, outParam, of);
        args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
    }

    // vector
    {
        int i = 3819;
        TArray<FVector> inParam = {FVector(1,2,3), FVector(4,5,6)};
        float f = 117.880;
        FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inParam), f);
        recorder->Note(_T("tester"), _T("send"), *args);
        callee->VectorIn(i, inParam, f);
        recorder->Note(_T("tester"), _T("recv"), _T("None"));
    }
    {
        int i = 7777;
        TArray<FVector> outParam;
        float f;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        callee->VectorOut(i, outParam, f);
        args = FString::Printf(_T("%s,%.3f"), *Str(outParam), f);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 5110;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        TArray<FVector> retParam = callee->VectorRet(i);
        args = FString::Printf(_T("%s"), *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 99411;
        TArray<FVector> inParam = {FVector(10,11,12),FVector(13,14,15),FVector(16,17,18),FVector(19,20,-21)};
        FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
        recorder->Note(_T("tester"), _T("send"), args);
        float of = 0.0f;
        TArray<FVector> retParam, outParam;
        retParam = callee->VectorInOutRet(i, inParam, outParam, of);
        args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
    }

    // string
    {
        int i = 786;
        TArray<FString> inParam = {_T("Rachael"), _T("Jacob"), _T("Nathan"), _T("Adam")};
        float f = 3.142;
        FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inParam), f);
        recorder->Note(_T("tester"), _T("send"), *args);
        callee->StringIn(i, inParam, f);
        recorder->Note(_T("tester"), _T("recv"), _T("None"));
    }
    {
        int i = 12321;
        TArray<FString> outParam;
        float f;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        callee->StringOut(i, outParam, f);
        args = FString::Printf(_T("%s,%.3f"), *Str(outParam), f);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 17761;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        TArray<FString> retParam = callee->StringRet(i);
        args = FString::Printf(_T("%s"), *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 73716;
        TArray<FString> inParam = {_T("One"), _T("Two"), _T("Three"), _T("Four"), _T("Five"), _T("Six")};
        FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
        recorder->Note(_T("tester"), _T("send"), args);
        float of = 0.0f;
        TArray<FString> retParam, outParam;
        retParam = callee->StringInOutRet(i, inParam, outParam, of);
        args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
    }

    // actor
    {
        int i = 13;
        TArray<AParamActor *> inParam;
        inParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Joe")));
        inParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Fred")));
        inParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Jared")));
        inParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Ed")));
        float f = -689.123;
        FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inParam), f);
        recorder->Note(_T("tester"), _T("send"), *args);
        callee->ActorIn(i, inParam, f);
        recorder->Note(_T("tester"), _T("recv"), _T("None"));
        AParamActor::DestroyActors(GetWorld(), inParam);
    }
    {
        int i = 7455;
        TArray<AParamActor*> outParam;
        float f;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        callee->ActorOut(i, outParam, f);
        args = FString::Printf(_T("%s,%.3f"), *Str(outParam), f);
        recorder->Note(_T("tester"), _T("recv"), args);
        AParamActor::DestroyActors(GetWorld(), outParam);
    }
    {
        int i = 311111;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        TArray<AParamActor*> retParam = callee->ActorRet(i);
        args = FString::Printf(_T("%s"), *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
        AParamActor::DestroyActors(GetWorld(), retParam);
    }
    {
        int i = 8675309;
        TArray<AParamActor *> inParam;
        inParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Larry")));
        inParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Curly")));
        inParam.Emplace(AParamActor::SpawnWithName(GetWorld(), _T("Moe")));
        FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
        recorder->Note(_T("tester"), _T("send"), args);
        float of = 0.0f;
        TArray<AParamActor *> retParam, outParam;
        retParam = callee->ActorInOutRet(i, inParam, outParam, of);
        args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
        AParamActor::DestroyActors(GetWorld(), inParam);
        AParamActor::DestroyActors(GetWorld(), outParam);
        AParamActor::DestroyActors(GetWorld(), retParam);
    }

    // struct
    {
        int i = 1887;
        TArray<FTestStruct> inParam;
        FTestStruct ts;
        ts.name = _T("Fingers"); ts.number = 10; inParam.Emplace(ts);
        ts.name = _T("Toes"); ts.number = 11; inParam.Emplace(ts);
        ts.name = _T("knees"); ts.number = 12; inParam.Emplace(ts);
        ts.name = _T("elboWS"); ts.number = 99; inParam.Emplace(ts);
        float f = -271.122;
        FString args = FString::Printf(_T("%d,%s,%.3f"), i, *Str(inParam), f);
        recorder->Note(_T("tester"), _T("send"), *args);
        callee->StructIn(i, inParam, f);
        recorder->Note(_T("tester"), _T("recv"), _T("None"));
    }
    {
        int i = 1234567;
        TArray<FTestStruct> outParam;
        float f;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        callee->StructOut(i, outParam, f);
        args = FString::Printf(_T("%s,%.3f"), *Str(outParam), f);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 10242048;
        FString args = FString::Printf(_T("%d"), i);
        recorder->Note(_T("tester"), _T("send"), args);
        TArray<FTestStruct> retParam = callee->StructRet(i);
        args = FString::Printf(_T("%s"), *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 6357;
        TArray<FTestStruct> inParam;
        FTestStruct ts;
        ts.name = _T("Dell"); ts.number = 107; inParam.Emplace(ts);
        ts.name = _T("HP"); ts.number = 1000; inParam.Emplace(ts);
        ts.name = _T("Razor"); ts.number = 201; inParam.Emplace(ts);
        FString args = FString::Printf(_T("%d,%s"), i, *Str(inParam));
        recorder->Note(_T("tester"), _T("send"), args);
        float of = 0.0f;
        TArray<FTestStruct> retParam, outParam;
        retParam = callee->StructInOutRet(i, inParam, outParam, of);
        args = FString::Printf(_T("%s,%.3f,%s"), *Str(outParam), of, *Str(retParam));
        recorder->Note(_T("tester"), _T("recv"), args);
    }
}

