init python:

  from ctypes import *
  import platform
  import os
  import sys

  class AmadeusCoreEngine(AmadeusEngine):
    """
    Primary cross-platform engine for Amadeus.
    """

    def __init__(self, channel_limit, version):
      """
      Initialize FMOD.

      Args:
        channel_limit (int): The maximum number of channels allowed to be registered.
        version (int): The version of FMOD loaded via the pre-compiled libraries.
      """
      self.__channels = {}

      if platform.system() == 'Windows':
        fmod_lib = 'fmod.dll'
      elif platform.system() == 'Linux':
        fmod_lib = 'libfmod.so'
      elif platform.system() == 'Darwin':
        arch = platform.architecture()[0]
        if arch == '32bit':
          # There is no 32 bit FMOD library for Mac OS
          raise RuntimeError('32-bit architecture for Mac OS is not supported')
        fmod_lib = 'libfmod.dylib'
      else:
        raise RuntimeError('Operating system is not supported')

      self.__api = CDLL(os.path.realpath(config.gamedir) + '/amadeus/lib/' + fmod_lib)

      self.__fmod = c_void_p()
      self.__call('System_Create', byref(self.__fmod), version)
      self.__call('System_Init', self.__fmod, channel_limit, 0x0, 0) # FMOD_INIT_NORMAL

    def shutdown(self):
      """
      Shut down the engine to free allocated resources.
      """
      self.__call('System_Release', self.__fmod)

    def tick(self):
      """
      Engine tick (20Hz).
      """
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
        self.__call('System_LockDSP', self.__fmod)

        rate = c_int()
        self.__call('System_GetSoftwareFormat', self.__fmod, byref(rate), 0, 0)
        samples = int(rate.value * fade)

        clock = c_ulonglong();
        self.__call('Channel_GetDSPClock', channel, 0, byref(clock))

        numpoints = c_int()
        self.__call('Channel_GetFadePoints', channel, byref(numpoints), 0, 0)
        if numpoints.value > 0:
          self.__call('Channel_SetDelay', channel, 0, 0, False)
          self.__call('Channel_RemoveFadePoints', channel, clock.value, clock.value + samples)

        self.__call('Channel_AddFadePoint', channel, clock.value, c_float(0.0))
        self.__call('Channel_AddFadePoint', channel, clock.value + samples, c_float(volume))

        self.__call('System_UnlockDSP', self.__fmod)
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
        self.__call('System_LockDSP', self.__fmod)

        rate = c_int()
        self.__call('System_GetSoftwareFormat', self.__fmod, byref(rate), 0, 0)
        samples = int(rate.value * fade)

        volume = c_float()
        self.__call('Channel_GetVolume', channel, byref(volume))

        clock = c_ulonglong();
        self.__call('Channel_GetDSPClock', channel, 0, byref(clock))

        numpoints = c_int()
        self.__call('Channel_GetFadePoints', channel, byref(numpoints), 0, 0)
        if numpoints.value > 0:
          self.__call('Channel_SetDelay', channel, 0, 0, False)
          self.__call('Channel_RemoveFadePoints', channel, clock.value, clock.value + samples)

        self.__call('Channel_AddFadePoint', channel, clock.value, volume)
        self.__call('Channel_AddFadePoint', channel, clock.value + samples, c_float(0.0))
        self.__call('Channel_SetDelay', channel, clock.value, clock.value + samples, True)

        self.__call('System_UnlockDSP', self.__fmod)
      else:
        self.__call('Channel_Stop', channel)
        self.__channels[channel_id] = None

      self.__call('System_Update', self.__fmod)

    def set_sound_volume(self, channel_id, volume):
      """
      Sets the sound volume on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to set the volume on.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
      """
      if not channel_id in self.__channels:
        return

      channel = self.__validate_channel(channel_id)

      if channel is None:
        return

      self.__call('Channel_SetVolumeRamp', channel, True)
      self.__call('Channel_SetVolume', channel, c_float(volume))

      self.__call('System_Update', self.__fmod)

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