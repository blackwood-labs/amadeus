#include <jni.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "fmod.hpp"
#include "amadeus.hpp"

FMOD::System  *fmod_system;
FMOD::Channel *channel_list[32];

void fn_check(FMOD_RESULT result) {
   if (result != FMOD_OK) {
      exit((int) result);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodInit(JNIEnv * env, jobject obj, jint jchannel_limit, jint jversion) {
   int channel_limit = (int) jchannel_limit;
   unsigned int version = (unsigned int) jversion;

   fn_check(FMOD::System_Create(&fmod_system, version));
   fn_check(fmod_system->init(channel_limit, FMOD_INIT_NORMAL, 0));
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodShutdown(JNIEnv * env, jobject obj) {
   fn_check(fmod_system->release());
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodTick(JNIEnv * env, jobject obj) {
   fn_check(fmod_system->update());
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodPlaySound(JNIEnv * env, jobject obj, jstring jfilepath, jint jchannel_id, jint jmode, jfloat jvolume, jfloat jfade) {
   const char * filepath = env->GetStringUTFChars(jfilepath, 0);
   int channel_id = (int) jchannel_id;
   FMOD_MODE mode = (FMOD_MODE) jmode;
   float volume = (float) jvolume;
   float fade = (float) jfade;

   FMOD::Sound *sound;
   fn_check(fmod_system->createSound(filepath, mode, 0, &sound));

   FMOD::Channel *channel;
   fn_check(fmod_system->playSound(sound, 0, false, &channel));
   channel_list[channel_id] = channel;

   if (fade > 0) {
      fn_check(fmod_system->lockDSP());

      int rate = 0;
      fn_check(fmod_system->getSoftwareFormat(&rate, 0, 0));
      unsigned long long samples = (rate * fade);

      unsigned long long clock = 0;
      fn_check(channel->getDSPClock(nullptr, &clock));

      unsigned int numpoints = 0;
      fn_check(channel->getFadePoints(&numpoints, 0, 0));
      if (numpoints > 0) {
         fn_check(channel->setDelay(0, 0, 0));
         fn_check(channel->removeFadePoints(clock, clock + samples));
      }

      fn_check(channel->addFadePoint(clock, 0.f));
      fn_check(channel->addFadePoint(clock + samples, volume));

      fn_check(fmod_system->unlockDSP());
   } else {
      fn_check(channel->setVolumeRamp(false));
      fn_check(channel->setVolume(volume));
   }

   fn_check(fmod_system->update());
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStopSound(JNIEnv * env, jobject obj, jint jchannel_id, jfloat jfade) {
   int channel_id = (int) jchannel_id;
   float fade = (float) jfade;

   FMOD::Channel *channel = channel_list[channel_id];

   if (!channel) {
      return;
   }

   if (fade > 0) {
      fn_check(fmod_system->lockDSP());

      int rate = 0;
      fn_check(fmod_system->getSoftwareFormat(&rate, 0, 0));
      unsigned long long samples = (rate * fade);

      float volume = 0.f;
      fn_check(channel->getVolume(&volume));

      unsigned long long clock = 0;
      fn_check(channel->getDSPClock(nullptr, &clock));

      unsigned int numpoints = 0;
      fn_check(channel->getFadePoints(&numpoints, 0, 0));
      if (numpoints > 0) {
         fn_check(channel->setDelay(0, 0, 0));
         fn_check(channel->removeFadePoints(clock, clock + samples));
      }

      fn_check(channel->addFadePoint(clock, volume));
      fn_check(channel->addFadePoint(clock + samples, 0.f));
      fn_check(channel->setDelay(0, clock + samples, true));

      fn_check(fmod_system->unlockDSP());
   } else {
      fn_check(channel->stop());
   }

   fn_check(fmod_system->update());
   channel_list[channel_id] = 0;
}