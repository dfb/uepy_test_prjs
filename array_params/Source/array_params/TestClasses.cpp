#include "TestClasses.h"

DECLARE_LOG_CATEGORY_EXTERN(ARRAY_PARAMS, Log, All);

#define LOG(format, ...) UE_LOG(ARRAY_PARAMS, Log, TEXT("[%s:%d] %s"), TEXT(__FUNCTION__), __LINE__, *FString::Printf(TEXT(format), ##__VA_ARGS__ ))

DEFINE_LOG_CATEGORY(ARRAY_PARAMS);

void ATestRecorder::Note(FString who, FString action, FString args)
{
    FString line = FString::Printf(_T("%s|%s|%s"), *who, *action, *args);
    lines.Emplace(line);
    //LOG("%s", *line);
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

void ATestActor::ActorIn_Implementation(int i, const TArray<AActor*>& actors, float f)
{
}

void ATestActor::ActorOut_Implementation(int i, TArray<AActor*>& actors, float& of)
{
}

TArray<AActor*> ATestActor::ActorRet_Implementation(int i)
{
    TArray<AActor *> ret;
    return ret;
}

TArray<AActor*> ATestActor::ActorInOutRet_Implementation(int i, const TArray<AActor*>& inActors, TArray<AActor*>& outActors, float& of)
{
    TArray<AActor *> ret;
    return ret;
}

void ATestActor::StructIn_Implementation(int i, const TArray<FTestStruct>& structs, float f)
{
}

void ATestActor::StructOut_Implementation(int i, TArray<FTestStruct>& structs, float& of)
{
}

TArray<FTestStruct> ATestActor::StructRet_Implementation(int i)
{
    TArray<FTestStruct> ret;
    return ret;
}

TArray<FTestStruct> ATestActor::StructInOutRet_Implementation(int i, const TArray<FTestStruct>& inStructs, TArray<FTestStruct>& outStructs, float& of)
{
    TArray<FTestStruct> ret;
    return ret;
}


void ATester::RunDebugTest(ATestRecorder *recorder, ATestActor *callee)
{

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
}

