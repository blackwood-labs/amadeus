init python:

  from ctypes import *
  import platform
  import os
  import sys

  class AmadeusCoreEngine(AmadeusEngine):
    """
    Primary cross-platform engine for Amadeus.
    """

    def __init__(self, channel_limit, event_limit, version):
      """
      Initialize FMOD.

      Args:
        channel_limit (int): The maximum number of channels allowed to be registered.
        event_limit (int): The maximum number of events allowed to be run at once.
        version (int): The version of FMOD loaded via the pre-compiled libraries.
      """
      self.__channels = {}
      self.__event_slots = {}

      if platform.system() == 'Windows':
        fmod_lib = 'fmod.dll'
        fmod_studio_lib = 'fmodstudio.dll'
      elif platform.system() == 'Linux':
        fmod_lib = 'libfmod.so'
        fmod_studio_lib = 'libfmodstudio.so'
      elif platform.system() == 'Darwin':
        arch = platform.architecture()[0]
        if arch == '32bit':
          # There is no 32 bit FMOD library for Mac OS
          raise RuntimeError('32-bit architecture for Mac OS is not supported')
        fmod_lib = 'libfmod.dylib'
        fmod_studio_lib = 'libfmodstudio.dylib'
      else:
        raise RuntimeError('Operating system is not supported')

      self.__api = CDLL(os.path.realpath(config.gamedir) + '/amadeus/lib/' + fmod_lib)
      self.__studio_api = CDLL(os.path.realpath(config.gamedir) + '/amadeus/lib/' + fmod_studio_lib)

      self.__fmod = c_void_p()
      self.__call('System_Create', byref(self.__fmod), version)
      self.__call('System_Init', self.__fmod, channel_limit + event_limit, 0x0, 0) # FMOD_INIT_NORMAL

      self.__fmod_studio = c_void_p()
      self.__call_studio('System_Create', byref(self.__fmod_studio), version)
      self.__call_studio('System_Initialize', self.__fmod_studio, channel_limit + event_limit, 0x0, 0x0, 0) # FMOD_STUDIO_INIT_NORMAL, FMOD_INIT_NORMAL

    def shutdown(self):
      """
      Shut down the engine to free allocated resources.
      """
      self.__call_studio('System_Release', self.__fmod_studio)
      self.__call('System_Release', self.__fmod)

    def tick(self):
      """
      Engine tick (20Hz).
      """
      self.__call_studio('System_Update', self.__fmod_studio)
      self.__call('System_Update', self.__fmod)

      for channel_id in self.__channels:
        self.__validate_channel(channel_id)

    def play_sound(self, filepath, channel_id, mode, volume, fade):
      """
      Plays sound from the given filepath on a specific channel.

      Args:
        filepath (str): The path of the file to load and play.
        channel_id (int): The numeric ID of the channel to play the sound on.
        mode (int): The mode flags which determine how to play the sound.
        volume (float): Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
        fade (float): Duration in seconds to fade in.

      Raises:
        FMODError: The result of any FMOD call was not FMOD_RESULT_OK
      """
      filepath = os.path.realpath(config.gamedir) + os.sep + filepath
      filepath = filepath.encode(sys.getfilesystemencoding())

      sound = c_void_p()
      self.__call('System_CreateSound', self.__fmod, filepath, mode, 0, byref(sound))

      channel = c_void_p()
      self.__call('System_PlaySound', self.__fmod, sound, 0, False, byref(channel))
      self.__channels[channel_id] = channel

      if fade > 0:
        self.__fade_channel_volume(channel, fade, 0.0, volume, False)
      else:
        self.__call('Channel_SetVolumeRamp', channel, False)
        self.__call('Channel_SetVolume', channel, c_float(volume))

      self.__call('System_Update', self.__fmod)

    def stop_sound(self, channel_id, fade):
      """
      Stops the sound on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to stop the sound on.
        fade (float): Duration in seconds to fade out.

      Raises:
        FMODError: The result of any FMOD call was not FMOD_RESULT_OK
      """
      if not channel_id in self.__channels:
        return

      channel = self.__validate_channel(channel_id)

      if channel is None:
        return

      if fade > 0:
        volume = c_float()
        self.__call('Channel_GetVolume', channel, byref(volume))

        self.__fade_channel_volume(channel, fade, volume.value, 0.0, True)
      else:
        self.__call('Channel_Stop', channel)
        self.__channels[channel_id] = None

      self.__call('System_Update', self.__fmod)

    def set_sound_volume(self, channel_id, volume, fade):
      """
      Sets the sound volume on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to set the volume on.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade.
      """
      if not channel_id in self.__channels:
        return

      channel = self.__validate_channel(channel_id)

      if channel is None:
        return

      if fade > 0:
        current_volume = c_float()
        self.__call('Channel_GetVolume', channel, byref(current_volume))

        self.__fade_channel_volume(channel, fade, current_volume.value, volume, False)
      else:
        self.__call('Channel_SetVolumeRamp', channel, True)
        self.__call('Channel_SetVolume', channel, c_float(volume))
        self.__call('System_Update', self.__fmod)

    def load_bank(self, filepath):
      """
      Loads a bank file into FMOD Studio.

      Args:
        filepath (str): The path of the bank file to load.

      Raises:
        FMODError: The result of any FMOD call was not FMOD_RESULT_OK
      """
      pass

    def load_event(self, name, slot_id):
      """
      Loads an event into memory and makes it ready for use.

      Args:
        name (str): The name of the event to load.
        slot_id (int): The event slot to load the event into.

      Raises:
        FMODError: The result of any FMOD call was not FMOD_RESULT_OK
      """
      pass

    def set_event_param(self, slot_id, key, value):
      """
      Sets a parameter value on an event.

      Args:
        slot_id (int): The event slot of the event to set the parameter on.
        key (str): The parameter key.
        value (float): The parameter value.

      Raises:
        RuntimeError: The given event slot has not been loaded.
        FMODError: The result of any FMOD call was not FMOD_RESULT_OK
      """
      pass

    def start_event(self, slot_id, volume):
      """
      Starts an event.

      Args:
        slot_id (int): The event slot of the event to start.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.

      Raises:
        RuntimeError: The given event slot has not been loaded.
        FMODError: The result of any FMOD call was not FMOD_RESULT_OK
      """
      pass

    def stop_event(self, slot_id):
      """
      Stops an event in the given slot.

      Args:
        slot_id (int): The event slot of the event to stop.

      Raises:
        FMODError: The result of any FMOD call was not FMOD_RESULT_OK
      """
      pass

    def set_event_volume(self, slot_id, volume):
      """
      Sets the volume for an event in the given slot.

      Args:
        slot_id (int): The event slot of the event to set the volume for.
        volume (float): Relative volume percent, where 1.0 = 100% and 0.0 = 0%.

      Raises:
        RuntimeError: The given event slot has not been loaded.
      """
      pass

    def __call(self, fn, *args):
      """
      Makes a call to the FMOD library and validates the result was successful.

      Args:
        fn (string): The function name to call.
        args: Arguments to the function.

      Raises:
        FMODError: The result was not FMOD_RESULT_OK
      """
      result = getattr(self.__api, 'FMOD_' + fn)(*args)

      if result != 0x0: # FMOD_RESULT_OK
        raise FMODError(result)

    def __call_studio(self, fn, *args):
      """
      Makes a call to the FMOD Studio library and validates the result was successful.

      Args:
        fn (string): The function name to call.
        args: Arguments to the function.

      Raises:
        FMODError: The result was not FMOD_RESULT_OK
      """
      result = getattr(self.__studio_api, "FMOD_Studio_" + fn)(*args)

      if result != 0x0: # FMOD_RESULT_OK
        raise FMODError(result)

    def __validate_channel(self, channel_id):
      """
      Validate that a channel is still valid and functional, and if not, kill it.

      Args:
        channel_id (int): The numberic ID of the channel to validate.

      Returns:
        The valid channel dict, or None if invalid
      """
      channel = self.__channels[channel_id]
      if channel is None:
        return None

      try:
        isPlaying = c_bool()
        self.__call('Channel_IsPlaying', channel, byref(isPlaying))
        if not isPlaying.value:
          self.__channels[channel_id] = None
          return None
      except FMODError as err:
        if err.result == 30: # FMOD_ERR_INVALID_HANDLE
          # Probably stopped on its own
          self.__channels[channel_id] = None
          return None

        raise err

      return channel

    def __fade_channel_volume(self, channel, time, vol_start, vol_end, close=False):
      """
      fades a channel's volume from one value to another.

      Args:
        channel (channel pointer): The channel to fade.
        time (float): Duration of the fade in seconds.
        vol_start (float): Volume at the beginning of the fade.
        vol_end (float): Volume at the end of the fade.

      Raises:
        FMODError: The result was not FMOD_RESULT_OK
      """
      self.__call('System_LockDSP', self.__fmod)

      rate = c_int()
      self.__call('System_GetSoftwareFormat', self.__fmod, byref(rate), 0, 0)
      samples = int(rate.value * time)

      clock = c_ulonglong()
      self.__call('Channel_GetDSPClock', channel, 0, byref(clock))

      numpoints = c_int()
      self.__call('Channel_GetFadePoints', channel, byref(numpoints), 0, 0)
      if numpoints.value > 0:
        self.__call('Channel_SetDelay', channel, 0, 0, False)
        self.__call('Channel_RemoveFadePoints', channel, clock.value, clock.value + samples)

      self.__call('Channel_AddFadePoint', channel, clock.value, c_float(vol_start))
      self.__call('Channel_AddFadePoint', channel, clock.value + samples, c_float(vol_end))
      if close:
        self.__call('Channel_SetDelay', channel, clock.value, clock.value + samples, True)

      self.__call('System_UnlockDSP', self.__fmod)
