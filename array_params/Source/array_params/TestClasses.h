#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TestClasses.generated.h"

// helps record events in C++, BP, or Python
UCLASS()
class ARRAY_PARAMS_API ATestRecorder : public AActor
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
class ARRAY_PARAMS_API ATestActor : public AActor
{
	GENERATED_BODY()

protected:
    UPROPERTY(BlueprintReadOnly) ATestRecorder *recorder;
	
public:	
    UFUNCTION(BlueprintCallable) void SetRecorder(ATestRecorder *r) { recorder = r; }
    UFUNCTION(BlueprintCallable) ATestRecorder *GetRecorder() { return recorder; }

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void IntIn(int i, const TArray<int32>& ints, float f);
    void IntIn_Implementation(int i, const TArray<int32>& ints, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void IntOut(int i, TArray<int32>& ints, float& of);
    void IntOut_Implementation(int i, TArray<int32>& ints, float& of);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<int32> IntRet(int i);
    TArray<int32> IntRet_Implementation(int i);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<int32> IntInOutRet(int i, const TArray<int32>& inInts, TArray<int32>& outInts, float& of);
    TArray<int32> IntInOutRet_Implementation(int i, const TArray<int32>& inInts, TArray<int32>& outInts, float& of);

};

// runs a series of tests against a test actor
UCLASS()
class ARRAY_PARAMS_API ATester : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable) void RunTests(ATestRecorder *r, ATestActor *callee);
    UFUNCTION(BlueprintCallable) void RunDebugTest(ATestRecorder *r, ATestActor *callee);
};

