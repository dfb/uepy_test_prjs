#include "TestClasses.h"

DECLARE_LOG_CATEGORY_EXTERN(OUTPUT_PARAMS, Log, All);

#define LOG(format, ...) UE_LOG(OUTPUT_PARAMS, Log, TEXT("[%s:%d] %s"), TEXT(__FUNCTION__), __LINE__, *FString::Printf(TEXT(format), ##__VA_ARGS__ ))

DEFINE_LOG_CATEGORY(OUTPUT_PARAMS);

// default C++ impl of call tests
void ATestActor::M000_Implementation()
{
    recorder->Note(_T("M000"), _T("recv"), _T(""));
}

void ATestActor::M100_Implementation(int i)
{
    recorder->Note(_T("M100"), _T("recv"), *FString::Printf(_T("%d"), i));
}

void ATestActor::M200_Implementation(int i, float f)
{
    recorder->Note(_T("M200"), _T("recv"), *FString::Printf(_T("%d,%.03f"), i, f));
}

float ATestActor::M001_Implementation()
{
    recorder->Note(_T("M001"), _T("recv"), _T(""));
    return 99.5;
}

float ATestActor::M101_Implementation(int i)
{
    recorder->Note(_T("M101"), _T("recv"), *FString::Printf(_T("%d"), i));
    return i / 2.0f;
}

float ATestActor::M201_Implementation(int i, float f)
{
    recorder->Note(_T("M201"), _T("recv"), *FString::Printf(_T("%d,%.03f"), i, f));
    return i * f;
}

void ATestActor::M010_Implementation(int& oi)
{
    recorder->Note(_T("M010"), _T("recv"), _T(""));
    oi = 71;
}

void ATestActor::M110_Implementation(int i, int& oi)
{
    recorder->Note(_T("M110"), _T("recv"), *FString::Printf(_T("%d"), i));
    oi = i * 2;
}

void ATestActor::M210_Implementation(int i, float f, int& oi)
{
    recorder->Note(_T("M210"), _T("recv"), *FString::Printf(_T("%d,%.03f"), i, f));
    oi = int(i * f);
}

float ATestActor::M011_Implementation(int& oi)
{
    recorder->Note(_T("M011"), _T("recv"), _T(""));
    oi = 15;
    return 4.321;
}

float ATestActor::M111_Implementation(int i, int& oi)
{
    recorder->Note(_T("M111"), _T("recv"), *FString::Printf(_T("%d"), i));
    oi = i/2;
    return i/2.0;
}

float ATestActor::M211_Implementation(int i, float f, int& oi)
{
    recorder->Note(_T("M211"), _T("recv"), *FString::Printf(_T("%d,%.03f"), i, f));
    oi = i/int(f);
    return 1.0 * i / f;
}

void ATestActor::M020_Implementation(int& oi, float& of)
{
    recorder->Note(_T("M020"), _T("recv"), _T(""));
    oi = 11;
    of = 9.111;
}

void ATestActor::M120_Implementation(int i, int& oi, float& of)
{
    recorder->Note(_T("M120"), _T("recv"), *FString::Printf(_T("%d"), i));
    oi = i*2;
    of = i*3.5;
}

void ATestActor::M220_Implementation(int i, float f, int& oi, float& of)
{
    recorder->Note(_T("M220"), _T("recv"), *FString::Printf(_T("%d,%.03f"), i, f));
    oi = i + int(f);
    of = i+f;
}

float ATestActor::M021_Implementation(int& oi, float& of)
{
    recorder->Note(_T("M021"), _T("recv"), _T(""));
    oi = 99;
    of = 98.765f;
    return 4.321f;
}

float ATestActor::M121_Implementation(int i, int& oi, float& of)
{
    recorder->Note(_T("M121"), _T("recv"), *FString::Printf(_T("%d"), i));
    oi = i*2;
    of = i/10.0f;
    return i/7.0;
}

float ATestActor::M221_Implementation(int i, float f, int& oi, float& of)
{
    recorder->Note(_T("M221"), _T("recv"), *FString::Printf(_T("%d,%.03f"), i, f));
    oi = i*3;
    of = f*2.0;
    return i*3*f*2.0;
}

void ATestRecorder::Note(FString who, FString action, FString args)
{
    FString line = FString::Printf(_T("%s|%s|%s"), *who, *action, *args);
    lines.Emplace(line);
    //LOG("%s", *line);
}

void ATester::RunDebugTest(ATestRecorder *recorder, ATestActor *callee)
{

}

void ATester::RunTests(ATestRecorder *recorder, ATestActor *callee)
{
    int i=0;
    float f=0.0f;

    // no out params
    recorder->Note(_T("tester"), _T("send"), _T(""));
    callee->M000();
    recorder->Note(_T("tester"), _T("recv"), _T("None"));

    recorder->Note(_T("tester"), _T("send"), _T("55"));
    callee->M100(55);
    recorder->Note(_T("tester"), _T("recv"), _T("None"));

    recorder->Note(_T("tester"), _T("send"), _T("17,2.500"));
    callee->M200(17, 2.5);
    recorder->Note(_T("tester"), _T("recv"), _T("None"));

    recorder->Note(_T("tester"), _T("send"), _T(""));
    f = callee->M001();
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%.3f"), f));

    recorder->Note(_T("tester"), _T("send"), _T("13"));
    f = callee->M101(13);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%.3f"), f));

    recorder->Note(_T("tester"), _T("send"), _T("2,7.500"));
    f = callee->M201(2, 7.5);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%.3f"), f));

    // 1 output param
    recorder->Note(_T("tester"), _T("send"), _T(""));
    callee->M010(i);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d"), i));

    recorder->Note(_T("tester"), _T("send"), _T("80"));
    callee->M110(80, i);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d"), i));

    recorder->Note(_T("tester"), _T("send"), _T("20,2.500"));
    callee->M210(20, 2.5, i);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d"), i));

    recorder->Note(_T("tester"), _T("send"), _T(""));
    f = callee->M011(i);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f"), i, f));

    recorder->Note(_T("tester"), _T("send"), _T("53"));
    f = callee->M111(53, i);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f"), i, f));

    recorder->Note(_T("tester"), _T("send"), _T("17,3.500"));
    f = callee->M211(17, 3.5, i);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f"), i, f));

    // 2 output params
    recorder->Note(_T("tester"), _T("send"), _T(""));
    callee->M020(i, f);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f"), i, f));

    recorder->Note(_T("tester"), _T("send"), _T("7"));
    callee->M120(7, i, f);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f"), i, f));

    recorder->Note(_T("tester"), _T("send"), _T("9,3.577"));
    callee->M220(9, 3.577, i, f);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f"), i, f));

    float r;
    recorder->Note(_T("tester"), _T("send"), _T(""));
    r = callee->M021(i, f);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f,%.3f"), i, f, r));

    recorder->Note(_T("tester"), _T("send"), _T("43"));
    r = callee->M121(43, i, f);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f,%.3f"), i, f, r));

    recorder->Note(_T("tester"), _T("send"), _T("7,8.215"));
    r = callee->M221(7, 8.215, i, f);
    recorder->Note(_T("tester"), _T("recv"), *FString::Printf(_T("%d,%.3f,%.3f"), i, f, r));
}

