init python:

  class Amadeus():
    """
    Amadeus sound engine.
    """

    def __init__(self):
      self.__channel_list = []
      self.__engine = AmadeusCoreEngine()

    def get_engine(self):
      """
      Accessor to get the active engine.

      Returns:
        The active engine.
      """
      return self.__engine

    def register_channel(self, name, mixer):
      """
      Registers a new channel which can be used to play simple sounds.

      Args:
        name (str): The name of the channel.
        mixer (str): The name of the Ren'Py mixer associated with the channel.

      Raises:
        ValueError: The specific Ren'Py mixer does not exist.
      """
      if not mixer in renpy.music.get_all_mixers():
        raise ValueError('Unknown Ren\'Py mixer: ' + str(mixer))

      # Avoid duplicate registrations
      for channel in self.__channel_list:
        if channel['name'] == name:
          return

      channel = {
        'id': len(self.__channel_list),
        'name': name,
        'mixer': mixer,
        'volume': 1.0,
      }

      self.__channel_list.append(channel)

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
      if not renpy.exists(filepath):
        raise ValueError('File does not exist: ' + str(filepath))

      channel = self.__get_channel(channel)
      channel['volume'] = volume

      relative_volume = volume * self.__get_mixer_volume(channel['mixer'])

      self.stop_sound(channel['name'])
      self.__engine.play_sound(filepath, channel['id'], loop, relative_volume, fade)

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
      self.__engine.stop_sound(channel['id'], fade)

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