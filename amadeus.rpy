init python:

  class Amadeus():
    """
    Amadeus sound engine.
    """

    def __init__(self, channel_limit=8, version=0x00020299, default_channels=True):
      self.__channel_limit = channel_limit
      self.__channel_list = []
      self.__version = version
      self.__mixer_volume = {}

      if default_channels:
        self.register_default_channels()

      if renpy.android:
        # The FMOD library expects to be loaded via Android JNI
        # It encounters an ill-defined internal error when loading via python CDLL
        # Therefore, we implement a separate engine implementation for Android
        try:
          self.__engine = AmadeusAndroidEngine(channel_limit, version)
        except NameError:
          # If the jnius library isn't available, try loading the core engine instead
          self.__engine = AmadeusCoreEngine(channel_limit, version)
      else:
        self.__engine = AmadeusCoreEngine(channel_limit, version)

      # Ensure that the engine is properly shut down when reloading and exiting
      if not self.shutdown in config.quit_callbacks:
        config.quit_callbacks.append(self.shutdown)

      # Ensure that the engine is properly shut down when reloading and exiting
      if not self.shutdown in config.periodic_callbacks:
        config.periodic_callbacks.append(self.tick)

      # Restore state when loading
      if not self.load in config.after_load_callbacks:
        config.after_load_callbacks.append(self.load)

    def save(self):
      """
      Saves the current state of the engine to a global variable.

      This allows the default Ren'Py save functionality to kick in and persist
      the active engine state to the save file.
      """
      global AMADEUS_STATE
      if not 'AMADEUS_STATE' in globals():
        AMADEUS_STATE = {}

      AMADEUS_STATE['channel_list'] = self.__channel_list

    def load(self):
      """
      Load state from the global variable into the engine.

      If there are any active channels, restart playing sound on those channels.
      """
      global AMADEUS_STATE

      # Stop all sounds without affecting state
      for channel in self.__channel_list:
        self.__engine.stop_sound(channel['id'], 0.0)

      self.__channel_list = AMADEUS_STATE['channel_list']
      for channel in self.__channel_list:
        if channel['data'] is not None:
          data = channel['data']
          data[3] = channel['volume'] # Override volume with current value
          self.play_sound(*data)

    def shutdown(self):
      """
      Shut down the engine to free allocated resources.
      """
      self.__engine.shutdown()

    def tick(self):
      """
      Engine tick (20Hz).
      """
      self.__engine.tick()
      self.__sync_mixer_volume()

    def get_engine(self):
      """
      Accessor to get the active engine.

      Returns:
        The active engine.
      """
      return self.__engine

    def get_channel_limit(self):
      """
      Accessor to get the channel limit.

      Returns:
        The channel limit.
      """
      return self.__channel_limit

    def register_channel(self, name, mixer):
      """
      Registers a new channel which can be used to play simple sounds.

      Args:
        name (str): The name of the channel.
        mixer (str): The name of the Ren'Py mixer associated with the channel.

      Raises:
        RuntimeError: Attempted to register more than the maximum number of channels.
      """
      if len(self.__channel_list) == self.__channel_limit:
        raise RuntimeError('Exceeded maximum number of channels')

      # Avoid duplicate registrations
      for channel in self.__channel_list:
        if channel['name'] == name:
          return

      channel = {
        'id': len(self.__channel_list),
        'name': name,
        'mixer': mixer,
        'volume': 1.0,
        'data': None,
      }

      self.__channel_list.append(channel)

    def register_default_channels(self):
      """
      Registers the default set of channels (music, sound, voice).
      """
      self.register_channel("sound", "sfx")
      self.register_channel("music", "music")
      self.register_channel("voice", "voice")

    def get_channels(self):
      """
      Accessor to get registered channels.

      Returns:
        The list of registered channels.
      """
      channels = []
      for channel in self.__channel_list:
        del channel['id']
        del channel['volume']
        del channel['data']
        channels.append(channel)
      return channels

    def clear_channels(self):
      """
      Clear ths list of registered channels.
      """
      self.__channel_list = []

    def play_sound(self, filepath, channel=None, loop=False, volume=1.0, fade=0.0):
      """
      Plays sound from the given filepath on a specific channel.

      Args:
        filepath (str): The path of the file to load and play.
        channel (str): The channel to play the sound on (uses first registered channel if None).
        loop (bool): Whether or not the sound should loop.
        volume (float): Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
        fade (float): Duration in seconds to fade in.

      Raises:
        ValueError: The specified file or channel does not exist.
      """
      if not renpy.loadable(filepath):
        raise ValueError('File does not exist: ' + str(filepath))

      self.stop_sound(channel)

      channel = self.__get_channel(channel)
      channel['volume'] = volume
      channel['data'] = [filepath, channel['name'], loop, volume, fade]
      self.save()

      mode = (0x0 | 0x02000000 | 0x08000000) # FMOD_DEFAULT | FMOD_IGNORETAGS | FMOD_LOWMEM;
      if loop:
        mode = (mode | 0x00000002) # FMOD_LOOP_NORMAL

      relative_volume = volume * self.__get_mixer_volume(channel['mixer'])

      self.__engine.play_sound(filepath, channel['id'], mode, relative_volume, fade)

    def stop_sound(self, channel=None, fade=0.0):
      """
      Stops the sound on the given channel.

      Args:
        channel (str): The channel to stop the sound on (uses first registered channel if None).
        fade (float): Duration in seconds to fade out.

      Raises:
        ValueError: The specified channel does not exist.
      """
      channel = self.__get_channel(channel)
      channel['data'] = None
      self.__engine.stop_sound(channel['id'], fade)
      self.save()

    def stop_all_sounds(self, fade=0.0):
      """
      Stops sounds on all channels.

      Args:
        fade (float): Duration in seconds to fade out.
      """
      for channel in self.__channel_list:
        self.stop_sound(channel['name'], fade)

    def set_sound_volume(self, volume, channel=None):
      """
      Sets the sound volume on the given channel.

      Args:
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        channel (str): The channel to set the volume on (uses first registered channel if None).

      Raises:
        ValueError: The specified channel does not exist.
      """
      channel = self.__get_channel(channel)
      channel['volume'] = volume

      relative_volume = volume * self.__get_mixer_volume(channel['mixer'])

      self.__engine.set_sound_volume(channel['id'], relative_volume)
      self.save()

    def __get_channel(self, name):
      """
      Retrieves the channel with the given name.

      Args:
        name (str): The name of the channel to return.

      Returns:
        A dict containing the details of the channel.

      Raises:
        ValueError: The specified channel does not exist.
      """
      if name is None:
        return self.__channel_list[0]

      for channel in self.__channel_list:
        if channel['name'] == name:
          return channel

      raise ValueError('Unknown Amadeus channel: ' + str(name))

    def __get_mixer_volume(self, mixer):
      """
      Gets the current volume level of the specified Ren'Py mixer.

      Args:
        mixer (str): The name of the Ren'Py mixer fetch the volume for.

      Returns:
        The current sound level of the specified Ren'Py mixer.

      Raises:
        ValueError: The specified Ren'Py mixer does not exist.
      """
      if not mixer in renpy.music.get_all_mixers():
        raise ValueError('Unknown Ren\'Py mixer: ' + str(mixer))

      muted = _preferences.get_mute(mixer)
      if muted:
        return 0.0

      return _preferences.get_volume(mixer)

    def __set_mixer_volume(self, mixer, volume):
      """
      Sets the volume level for all channels associated with the specified Ren'Py mixer.

      Args:
        mixer (str): The name of the Ren'Py mixer fetch the volume for.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
      """
      for channel in self.__channel_list:
        if mixer == channel['mixer']:
          self.__engine.set_sound_volume(channel['id'], volume * channel['volume'])

    def __sync_mixer_volume(self):
      """
      Synchronize the volume of Ren'Py mixers with all associated channels.
      """
      for mixer in renpy.music.get_all_mixers():
        volume = self.__get_mixer_volume(mixer)
        if mixer not in self.__mixer_volume or volume != self.__mixer_volume[mixer]:
          self.__set_mixer_volume(mixer, volume)
          self.__mixer_volume[mixer] = volume
