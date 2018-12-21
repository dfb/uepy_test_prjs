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

USTRUCT(BlueprintType)
struct FTestStruct
{
    GENERATED_BODY();
    UPROPERTY(BlueprintReadWrite, EditAnywhere) FString name;
    UPROPERTY(BlueprintReadWrite, EditAnywhere) int number;
};

// this actor is used in the UObject parameter tests
UCLASS()
class ARRAY_PARAMS_API AParamActor : public AActor
{
    GENERATED_BODY()
    FString _name;
public:
    UFUNCTION(BlueprintCallable) void SetTestName(FString n) { _name = n; }
    UFUNCTION(BlueprintCallable) FString GetTestName() const { return _name; }

    UFUNCTION(BlueprintCallable, Meta=(DefaultToSelf="WorldContextObject", HidePin="WorldContextObject"))
    static void DestroyActors(UObject *WorldContextObject, const TArray<AParamActor *>& actors);

    UFUNCTION(BlueprintCallable, Meta=(DefaultToSelf="WorldContextObject", HidePin="WorldContextObject"))
    static AParamActor *SpawnWithName(UObject *WorldContextObject, FString withName);
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

    // int arrays
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void IntIn(int i, const TArray<int32>& ints, float f);
    void IntIn_Implementation(int i, const TArray<int32>& ints, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void IntOut(int i, TArray<int32>& ints, float& of);
    void IntOut_Implementation(int i, TArray<int32>& ints, float& of);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<int32> IntRet(int i);
    TArray<int32> IntRet_Implementation(int i);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<int32> IntInOutRet(int i, const TArray<int32>& inInts, TArray<int32>& outInts, float& of);
    TArray<int32> IntInOutRet_Implementation(int i, const TArray<int32>& inInts, TArray<int32>& outInts, float& of);

    // bool arrays
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void BoolIn(int i, const TArray<bool>& bools, float f);
    void BoolIn_Implementation(int i, const TArray<bool>& bools, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void BoolOut(int i, TArray<bool>& bools, float& of);
    void BoolOut_Implementation(int i, TArray<bool>& bools, float& of);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<bool> BoolRet(int i);
    TArray<bool> BoolRet_Implementation(int i);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<bool> BoolInOutRet(int i, const TArray<bool>& inBools, TArray<bool>& outBools, float& of);
    TArray<bool> BoolInOutRet_Implementation(int i, const TArray<bool>& inBools, TArray<bool>& outBools, float& of);

    // vector arrays
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void VectorIn(int i, const TArray<FVector>& vectors, float f);
    void VectorIn_Implementation(int i, const TArray<FVector>& vectors, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void VectorOut(int i, TArray<FVector>& vectors, float& of);
    void VectorOut_Implementation(int i, TArray<FVector>& vectors, float& of);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<FVector> VectorRet(int i);
    TArray<FVector> VectorRet_Implementation(int i);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<FVector> VectorInOutRet(int i, const TArray<FVector>& inVectors, TArray<FVector>& outVectors, float& of);
    TArray<FVector> VectorInOutRet_Implementation(int i, const TArray<FVector>& inVectors, TArray<FVector>& outVectors, float& of);

    // string arrays
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void StringIn(int i, const TArray<FString>& strings, float f);
    void StringIn_Implementation(int i, const TArray<FString>& strings, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void StringOut(int i, TArray<FString>& strings, float& of);
    void StringOut_Implementation(int i, TArray<FString>& strings, float& of);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<FString> StringRet(int i);
    TArray<FString> StringRet_Implementation(int i);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<FString> StringInOutRet(int i, const TArray<FString>& inStrings, TArray<FString>& outStrings, float& of);
    TArray<FString> StringInOutRet_Implementation(int i, const TArray<FString>& inStrings, TArray<FString>& outStrings, float& of);

    // UObject arrays (using Actors as the test object)
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void ActorIn(int i, const TArray<AParamActor*>& actors, float f);
    void ActorIn_Implementation(int i, const TArray<AParamActor*>& actors, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void ActorOut(int i, TArray<AParamActor*>& actors, float& of);
    void ActorOut_Implementation(int i, TArray<AParamActor*>& actors, float& of);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<AParamActor*> ActorRet(int i);
    TArray<AParamActor*> ActorRet_Implementation(int i);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<AParamActor*> ActorInOutRet(int i, const TArray<AParamActor*>& inActors, TArray<AParamActor*>& outActors, float& of);
    TArray<AParamActor*> ActorInOutRet_Implementation(int i, const TArray<AParamActor*>& inActors, TArray<AParamActor*>& outActors, float& of);

    // struct arrays (using FTestStruct as the test struct)
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void StructIn(int i, const TArray<FTestStruct>& structs, float f);
    void StructIn_Implementation(int i, const TArray<FTestStruct>& structs, float f);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) void StructOut(int i, TArray<FTestStruct>& structs, float& of);
    void StructOut_Implementation(int i, TArray<FTestStruct>& structs, float& of);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<FTestStruct> StructRet(int i);
    TArray<FTestStruct> StructRet_Implementation(int i);

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent) TArray<FTestStruct> StructInOutRet(int i, const TArray<FTestStruct>& inStructs, TArray<FTestStruct>& outStructs, float& of);
    TArray<FTestStruct> StructInOutRet_Implementation(int i, const TArray<FTestStruct>& inStructs, TArray<FTestStruct>& outStructs, float& of);
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

