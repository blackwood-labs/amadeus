#include <jni.h>

#ifndef _Included_net_blackwoodlabs_renpy_MusicEngine
#define _Included_net_blackwoodlabs_renpy_MusicEngine
#ifdef __cplusplus
extern "C" {
#endif

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodInit
  (JNIEnv *, jobject, jint, jint, jint);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodShutdown
  (JNIEnv *, jobject);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodTick
  (JNIEnv *, jobject);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodPlaySound
  (JNIEnv *, jobject, jstring, jint, jint, jfloat, jfloat);

JNIEXPORT bool JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodIsSoundPlaying
  (JNIEnv *, jobject, jint);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStopSound
  (JNIEnv *, jobject, jint, jfloat);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodSetSoundVolume
  (JNIEnv *, jobject, jint, jfloat, jfloat);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodLoadBank
  (JNIEnv *, jobject, jstring);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodLoadEvent
  (JNIEnv *, jobject, jstring, jint);

JNIEXPORT bool JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodIsEventLoaded
  (JNIEnv *, jobject, jint);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodSetEventParam
  (JNIEnv *, jobject, jint, jstring, jfloat);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStartEvent
  (JNIEnv *, jobject, jint, jfloat, jfloat);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStopEvent
  (JNIEnv *, jobject, jint, jfloat);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodSetEventVolume
  (JNIEnv *, jobject, jint, jfloat, jfloat);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodEnsureEventTimeElapsed
  (JNIEnv *, jobject, jint, jfloat);

#ifdef __cplusplus
}
#endif
#endif