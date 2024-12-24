#include <jni.h>
#include <stdio.h>
#include <string.h>
#include "fmod.hpp"
#include "fmod_studio.hpp"
#include "amadeus.hpp"

FMOD::System  *fmod_system;
FMOD::Studio::System  *fmod_studio_system;
FMOD::Channel *channel_list[32];
FMOD::Studio::EventInstance *event_slots[32];
FMOD::ChannelControl *event_channels[32];
int channel_limit = 32;
int event_limit = 32;

void fn_check(FMOD_RESULT result) {
   if (result != FMOD_OK) {
      throw (result);
   }
}

FMOD::Channel* validate_channel(int channel_id) {
   FMOD::Channel *channel = channel_list[channel_id];
   if (!channel) {
      return channel;
   }

   bool isPlaying = 0;
   FMOD_RESULT result = channel->isPlaying(&isPlaying);
   if (result == FMOD_ERR_INVALID_HANDLE) {
      // Probably stopped on its own
      channel_list[channel_id] = 0;
      return nullptr;
   } else {
      fn_check(result);
   }

   if (!isPlaying) {
      channel_list[channel_id] = 0;
      return nullptr;
   }

   return channel;
}

FMOD::Studio::EventInstance* validate_event_slot(int slot_id) {
   FMOD::Studio::EventInstance *event = event_slots[slot_id];
   if (!event) {
      return event;
   }

   FMOD::ChannelControl *channel = event_channels[slot_id];
   if (!channel) {
      return event;
   }

   bool is_playing = 0;
   FMOD_RESULT result = channel->isPlaying(&is_playing);
   if (result != FMOD_OK) {
      if (result != FMOD_ERR_INVALID_HANDLE) {
         fn_check(result); // Something else went wrong, handle it
      }

      // Channel is unavailable, kill the event
      fn_check(event->stop(FMOD_STUDIO_STOP_ALLOWFADEOUT));
      fn_check(fmod_studio_system->update());
      event_slots[slot_id] = 0;
      event_channels[slot_id] = 0;
      return nullptr;
   }

   // Channel has stopped playing, assume the event has stopped and kill it
   if (!is_playing) {
      fn_check(event->stop(FMOD_STUDIO_STOP_ALLOWFADEOUT));
      fn_check(fmod_studio_system->update());
      event_slots[slot_id] = 0;
      event_channels[slot_id] = 0;
      return nullptr;
   }

   return event;
}

void fade_channel_volume(FMOD::ChannelControl *channel, float time, float vol_start, float vol_end, bool close) {
   fn_check(fmod_system->lockDSP());

   int rate = 0;
   fn_check(fmod_system->getSoftwareFormat(&rate, 0, 0));
   unsigned long long samples = (rate * time);

   unsigned long long clock = 0;
   fn_check(channel->getDSPClock(nullptr, &clock));

   unsigned int numpoints = 0;
   fn_check(channel->getFadePoints(&numpoints, 0, 0));
   if (numpoints > 0) {
      fn_check(channel->setDelay(0, 0, 0));
      fn_check(channel->removeFadePoints(clock, clock + samples));
   }

   fn_check(channel->addFadePoint(clock, vol_start));
   fn_check(channel->addFadePoint(clock + samples, vol_end));
   if (close) {
      fn_check(channel->setDelay(0, clock + samples, true));
   }

   fn_check(fmod_system->unlockDSP());
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodInit(JNIEnv * env, jobject obj, jint jchannel_limit, jint jevent_limit, jint jversion) {
   channel_limit = (int) jchannel_limit;
   event_limit = (int) jevent_limit;
   unsigned int version = (unsigned int) jversion;

   try {
      fn_check(FMOD::System_Create(&fmod_system, version));
      fn_check(fmod_system->init(channel_limit + event_limit, FMOD_INIT_NORMAL, 0));

      fn_check(FMOD::Studio::System::create(&fmod_studio_system, version));
      fn_check(fmod_studio_system->initialize(channel_limit + event_limit, FMOD_STUDIO_INIT_NORMAL, FMOD_INIT_NORMAL, 0));
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodShutdown(JNIEnv * env, jobject obj) {
   try {
      fn_check(fmod_studio_system->release());
      fn_check(fmod_system->release());
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodTick(JNIEnv * env, jobject obj) {
   try {
      fn_check(fmod_studio_system->update());
      fn_check(fmod_system->update());

      for (int i=0; i<channel_limit; i++) {
         validate_channel(i);
      }

      for (int i=0; i<event_limit; i++) {
         validate_event_slot(i);
      }
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodPlaySound(JNIEnv * env, jobject obj, jstring jfilepath, jint jchannel_id, jint jmode, jfloat jvolume, jfloat jfade) {
   const char * filepath = env->GetStringUTFChars(jfilepath, 0);
   int channel_id = (int) jchannel_id;
   FMOD_MODE mode = (FMOD_MODE) jmode;
   float volume = (float) jvolume;
   float fade = (float) jfade;

   try {
      FMOD::Sound *sound;
      fn_check(fmod_system->createSound(filepath, mode, 0, &sound));

      FMOD::Channel *channel;
      fn_check(fmod_system->playSound(sound, 0, false, &channel));
      channel_list[channel_id] = channel;

      if (fade > 0) {
         fade_channel_volume(channel, fade, 0.f, volume, false);
      } else {
         fn_check(channel->setVolumeRamp(false));
         fn_check(channel->setVolume(volume));
      }

      fn_check(fmod_system->update());
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStopSound(JNIEnv * env, jobject obj, jint jchannel_id, jfloat jfade) {
   int channel_id = (int) jchannel_id;
   float fade = (float) jfade;

   try {
      FMOD::Channel *channel = validate_channel(channel_id);

      if (!channel) {
         return;
      }

      if (fade > 0) {
         float volume = 0.f;
         fn_check(channel->getVolume(&volume));

         fade_channel_volume(channel, fade, volume, 0.f, true);
      } else {
         fn_check(channel->stop());
         channel_list[channel_id] = 0;
      }

      fn_check(fmod_system->update());
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodSetSoundVolume(JNIEnv * env, jobject obj, jint jchannel_id, jfloat jvolume, jfloat jfade) {
   int channel_id = (int) jchannel_id;
   float volume = (float) jvolume;
   float fade = (float) jfade;

   try {
      FMOD::Channel *channel = validate_channel(channel_id);

      if (!channel) {
         return;
      }

      if (fade > 0) {
         float current_volume = 0.f;
         fn_check(channel->getVolume(&current_volume));

         fade_channel_volume(channel, fade, current_volume, volume, false);
      } else {
         fn_check(channel->setVolumeRamp(true));
         fn_check(channel->setVolume(volume));
      }

      fn_check(fmod_system->update());
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodLoadBank(JNIEnv * env, jobject obj, jstring jfilepath) {
   const char * filepath = env->GetStringUTFChars(jfilepath, 0);

   try {
      FMOD::Studio::Bank *bank;
      fn_check(fmod_studio_system->loadBankFile(filepath, FMOD_STUDIO_LOAD_BANK_NORMAL, &bank)); // No need to keep reference
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodLoadEvent(JNIEnv * env, jobject obj, jstring jname, jint jslot_id) {
   const char * name = env->GetStringUTFChars(jname, 0);
   int slot_id = (int) jslot_id;

   try {
      FMOD::Studio::EventDescription *event;
      FMOD::Studio::EventInstance *instance = event_slots[slot_id];
      if (instance) {
         return; // Already loaded
      }

      fn_check(fmod_studio_system->getEvent(name, &event));
      fn_check(event->createInstance(&instance));
      fn_check(fmod_studio_system->update());
      event_slots[slot_id] = instance;
      event_channels[slot_id] = 0;
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT bool JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodIsEventLoaded(JNIEnv * env, jobject obj, jint jslot_id) {
   int slot_id = (int) jslot_id;

   try {
      FMOD::Studio::EventInstance *event = validate_event_slot(slot_id);
      if (event) {
         return true;
      }

      return false;
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodSetEventParam(JNIEnv * env, jobject obj, jint jslot_id, jstring jkey, jfloat jvalue) {
   int slot_id = (int) jslot_id;
   const char * key = env->GetStringUTFChars(jkey, 0);
   float value = (float) jvalue;

   try {
      FMOD::Studio::EventInstance *event = validate_event_slot(slot_id);
      if (!event) {
         char buffer[50];
         sprintf(buffer, "Event has not been loaded: %d", slot_id);
         env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
      }

      fn_check(event->setParameterByName(key, value, false));
      fn_check(fmod_studio_system->update());
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStartEvent(JNIEnv * env, jobject obj, jint jslot_id, jfloat jvolume, jfloat jfade) {
   int slot_id = (int) jslot_id;
   float volume = (float) jvolume;
   float fade = (float) jfade;

   try {
      FMOD::Studio::EventInstance *event = event_slots[slot_id];
      if (!event) {
         char buffer[50];
         sprintf(buffer, "Event has not been loaded: %d", slot_id);
         env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
      }

      // Always set the event itself to full volume
      // We will manipulate the underlying channel volume instead
      fn_check(event->setVolume(1.f));
      fn_check(event->start());
      fn_check(fmod_studio_system->update());

      // Release immediately, since it holds no resources
      fn_check(event->release());
      fn_check(fmod_studio_system->update());

      // Wait for event to fully start
      FMOD_STUDIO_PLAYBACK_STATE state = FMOD_STUDIO_PLAYBACK_STARTING;
      while (state != FMOD_STUDIO_PLAYBACK_PLAYING) {
         fn_check(event->getPlaybackState(&state));
      }

      FMOD::ChannelGroup *channel;
      fn_check(event->getChannelGroup(&channel));

      // Wait for channel to start playing
      bool is_playing = 0;
      while (!is_playing) {
         fn_check(channel->isPlaying(&is_playing));
      }

      event_channels[slot_id] = channel;

      if (fade > 0) {
         fade_channel_volume(channel, fade, 0.f, volume, false);
      } else {
         fn_check(channel->setVolumeRamp(false));
         fn_check(channel->setVolume(volume));
      }

      fn_check(fmod_system->update());
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodStopEvent(JNIEnv * env, jobject obj, jint jslot_id, jfloat jfade) {
   int slot_id = (int) jslot_id;
   float fade = (float) jfade;

   try {
      FMOD::Studio::EventInstance *event = validate_event_slot(slot_id);
      if (!event) {
         return;
      }

      if (fade > 0) {
         FMOD::ChannelGroup *channel;
         fn_check(event->getChannelGroup(&channel));

         float volume;
         fn_check(channel->getVolume(&volume));

         fade_channel_volume(channel, fade, volume, 0.f, true);
         fn_check(fmod_system->update());
      } else {
         fn_check(event->stop(FMOD_STUDIO_STOP_ALLOWFADEOUT));
         fn_check(fmod_studio_system->update());
         event_slots[slot_id] = 0;
         event_channels[slot_id] = 0;
      }
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodSetEventVolume(JNIEnv * env, jobject obj, jint jslot_id, jfloat jvolume, jfloat jfade) {
   int slot_id = (int) jslot_id;
   float volume = (float) jvolume;
   float fade = (float) jfade;

   try {
      FMOD::Studio::EventInstance *event = validate_event_slot(slot_id);
      if (!event) {
         char buffer[50];
         sprintf(buffer, "Event has not been loaded: %d", slot_id);
         env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
      }

      FMOD_STUDIO_PLAYBACK_STATE state;
      fn_check(event->getPlaybackState(&state));
      if (state != FMOD_STUDIO_PLAYBACK_PLAYING) {
         return; // Tried to change volume on an unstarted or dead event
      }

      FMOD::ChannelGroup *channel;
      fn_check(event->getChannelGroup(&channel));

      if (fade > 0) {
         float current_volume;
         fn_check(channel->getVolume(&current_volume));

         fade_channel_volume(channel, fade, current_volume, volume, false);
      } else {
         fn_check(channel->setVolumeRamp(false));
         fn_check(channel->setVolume(volume));
      }

      fn_check(fmod_system->update());
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}

JNIEXPORT void JNICALL Java_net_blackwoodlabs_renpy_Amadeus_fmodEnsureEventTimeElapsed(JNIEnv * env, jobject obj, jint jslot_id, jfloat jtime) {
   int slot_id = (int) jslot_id;
   float time = (float) jtime;

   try {
      FMOD::Studio::EventInstance *event = validate_event_slot(slot_id);
      if (!event) {
         char buffer[50];
         sprintf(buffer, "Event has not been loaded: %d", slot_id);
         env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
      }

      int current_position;
      fn_check(event->getTimelinePosition(&current_position));

      int target_position = (time * 1000);
      if (current_position < target_position) {
         fn_check(event->setTimelinePosition(target_position));
         fn_check(fmod_studio_system->update());
      }
   } catch (FMOD_RESULT result) {
      char buffer[50];
      sprintf(buffer, "FMOD encountered an error: %d", (int) result);
      env->ThrowNew(env->FindClass("java/lang/Exception"), buffer);
   }
}