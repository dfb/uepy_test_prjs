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

FString StrIntArray(const TArray<int32>& array)
{
    TArray<FString> parts;
    for (int32 a : array)
        parts.Emplace(FString::Printf(_T("%d"), a));
    return FString::Printf(_T("[%s]"), *FString::Join(parts, _T(",")));
}

void NoteIntArray(ATestRecorder *tr, FString who, FString action, const TArray<int32>& array)
{
    tr->Note(*who, *action, *StrIntArray(array));
}

void ATestActor::IntIn_Implementation(int i, const TArray<int32>& ints, float f)
{
    FString args = FString::Printf(_T("%d,%s,%.3f"), i, *StrIntArray(ints), f);
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
    args = FString::Printf(_T("%s,%.3f"), *StrIntArray(ints), of);
    recorder->Note(_T("IntOut"), _T("send"), *args);
}

TArray<int32> ATestActor::IntRet_Implementation(int i)
{
    FString args = FString::Printf(_T("%d"), i);
    recorder->Note(_T("IntRet"), _T("recv"), *args);
    TArray<int32> ints = {101, 55, -4};
    args = StrIntArray(ints);
    recorder->Note(_T("IntRet"), _T("send"), *args);
    return ints;
}

TArray<int32> ATestActor::IntInOutRet_Implementation(int i, const TArray<int32>& inInts, TArray<int32>& outInts, float& of)
{
    FString args = FString::Printf(_T("%d,%s"), i, *StrIntArray(inInts));
    recorder->Note(_T("IntInOutRet"), _T("recv"), *args);
    of = 113.117;
    outInts.Empty();
    outInts.Emplace(-11);
    outInts.Emplace(37);
    outInts.Emplace(1011);
    outInts.Emplace(65535);
    TArray<int32> retInts = {16, 32, 64, 128, 256, 512};
    args = FString::Printf(_T("%s,%.3f,%s"), *StrIntArray(outInts), of, *StrIntArray(retInts));
    recorder->Note(_T("IntInOutRet"), _T("send"), *args);
    return retInts;
}

void ATester::RunDebugTest(ATestRecorder *recorder, ATestActor *callee)
{

}

void ATester::RunTests(ATestRecorder *recorder, ATestActor *callee)
{
    {
        TArray<int32> ints = {55, 57, 59, 61};
        int i = 10;
        float f = 3.5;
        FString args = FString::Printf(_T("%d,%s,%.3f"), i, *StrIntArray(ints), f);
        recorder->Note(_T("tester"), _T("send"), *args);
        callee->IntIn(i, ints, f);
        recorder->Note(_T("tester"), _T("recv"), _T("None"));
    }
    {
        TArray<int32> ints;
        float f;
        recorder->Note(_T("tester"), _T("send"), _T("13"));
        callee->IntOut(13, ints, f);
        FString args = FString::Printf(_T("%s,%.3f"), *StrIntArray(ints), f);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        recorder->Note(_T("tester"), _T("send"), _T("45"));
        TArray<int32> ints = callee->IntRet(45);
        FString args = StrIntArray(ints);
        recorder->Note(_T("tester"), _T("recv"), args);
    }
    {
        int i = 51;
        TArray<int32> inInts = {99, 89, 79, 69, 59, 49, 39, 29, 19, 9, -1};
        FString args = FString::Printf(_T("%d,%s"), i, *StrIntArray(inInts));
        recorder->Note(_T("tester"), _T("send"), args);
        float of = 0.0f;
        TArray<int32> retInts, outInts;
        retInts = callee->IntInOutRet(i, inInts, outInts, of);
        args = FString::Printf(_T("%s,%.3f,%s"), *StrIntArray(outInts), of, *StrIntArray(retInts));
        recorder->Note(_T("tester"), _T("recv"), args);
    }

}
