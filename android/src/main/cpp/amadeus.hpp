#include <jni.h>

#ifndef _Included_net_blackwoodlabs_renpy_MusicEngine
#define _Included_net_blackwoodlabs_renpy_MusicEngine
#ifdef __cplusplus
extern "C" {
#endif

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodInit
  (JNIEnv *, jobject, jint, jint);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodShutdown
  (JNIEnv *, jobject);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodTick
  (JNIEnv *, jobject);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodPlaySound
  (JNIEnv *, jobject, jstring, jint, jint, jfloat, jfloat);

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStopSound
  (JNIEnv *, jobject, jint, jfloat);

#ifdef __cplusplus
}
#endif
#endif