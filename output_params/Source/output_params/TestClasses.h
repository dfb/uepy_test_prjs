#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TestClasses.generated.h"

// helps record events in C++, BP, or Python
UCLASS()
class OUTPUT_PARAMS_API ATestRecorder : public AActor
{
    GENERATED_BODY()
    TArray<FString> lines;
    FString curTestName;
public:
    UFUNCTION(BlueprintCallable) FString GetLines() { return FString::Join(lines, _T("\n")); }
    UFUNCTION(BlueprintCallable) void Clear() { lines.Empty(); }
    UFUNCTION(BlueprintCallable) FString GetCurTestName() { return curTestName; }
    UFUNCTION(BlueprintCallable, CallInEditor) void Note(FString who, FString action, FString args);
    UFUNCTION(BlueprintCallable, CallInEditor) void Begin(FString testName) { curTestName = testName; }
    UFUNCTION(BlueprintCallable, CallInEditor, BlueprintNativeEvent) void End(const FString& expected);
    void End_Implementation(const FString& expected) {}
};

// the class used for testing - implements methods with various combinations of in/out/return params
UCLASS()
class OUTPUT_PARAMS_API ATestActor : public AActor
{
	GENERATED_BODY()

protected:
    UPROPERTY(BlueprintReadOnly) ATestRecorder *recorder;
	
public:	
    UFUNCTION(BlueprintCallable) void SetRecorder(ATestRecorder *r) { recorder = r; }
    UFUNCTION(BlueprintCallable) ATestRecorder *GetRecorder() { return recorder; }

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M000();
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M100(int i);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M200(int i, float f);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M001();
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M101(int i);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M201(int i, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M010(int& oi);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M110(int i, int& oi);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M210(int i, float f, int& oi);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M011(int& oi);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M111(int i, int& oi);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M211(int i, float f, int& oi);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M020(int& oi, float& of);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M120(int i, int& oi, float& of);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void M220(int i, float f, int& oi, float& of);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M021(int& oi, float& of);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M121(int i, int& oi, float& of);
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) float M221(int i, float f, int& oi, float& of);

    void M000_Implementation();
    void M100_Implementation(int i);
    void M200_Implementation(int i, float f);
    float M001_Implementation();
    float M101_Implementation(int i);
    float M201_Implementation(int i, float f);

    void M010_Implementation(int& oi);
    void M110_Implementation(int i, int& oi);
    void M210_Implementation(int i, float f, int& oi);
    float M011_Implementation(int& oi);
    float M111_Implementation(int i, int& oi);
    float M211_Implementation(int i, float f, int& oi);

    void M020_Implementation(int& oi, float& of);
    void M120_Implementation(int i, int& oi, float& of);
    void M220_Implementation(int i, float f, int& oi, float& of);
    float M021_Implementation(int& oi, float& of);
    float M121_Implementation(int i, int& oi, float& of);
    float M221_Implementation(int i, float f, int& oi, float& of);
};

// runs a series of tests against a test actor
UCLASS()
class OUTPUT_PARAMS_API ATester : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable) void RunTests(ATestRecorder *r, ATestActor *callee);
    UFUNCTION(BlueprintCallable) void RunDebugTest(ATestRecorder *r, ATestActor *callee);
};
