init python:
  class AmadeusChannel:
    """
    Representation of an individual sound channel.
    """

    def __init__(self, engine, id, name, mixer):
      self.__engine = engine
      self.__id = id
      self.__name = name
      self.__mixer = mixer
      self.__active = None

    def get_id(self):
      """
      Accessor for the channel id.

      Returns:
        The channel id.
      """
      return self.__id

    def get_name(self):
      """
      Accessor for the channel name.

      Returns:
        The channel name.
      """
      return self.__name

    def get_mixer(self):
      """
      Accessor for the channel mixer.

      Returns:
        The channel mixer.
      """
      return self.__mixer

    def now_playing(self):
      """
      Accessor for the details of the active playing sound.

      Returns:
        The details of the active playing sound as a dict.
      """
      return self.__active

    def play_sound(self, filepath, loop, volume, fade):
      """
      Plays sound from the given filepath.

      Args:
        filepath (str): The path of the file to load and play.
        loop (bool): Whether or not the sound should loop.
        volume (float): Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
        fade (float): Duration in seconds to fade in.
      """
      self.__active = {
        'filepath': filepath,
        'loop': loop,
        'volume': volume,
        'fade': fade,
      }

      mode = (0x0 | 0x02000000 | 0x08000000) # FMOD_DEFAULT | FMOD_IGNORETAGS | FMOD_LOWMEM;
      if loop:
        mode = (mode | 0x00000002) # FMOD_LOOP_NORMAL

      relative_volume = volume * renpy.game.preferences.volumes.get(self.__mixer, 1.0)

      if renpy.game.preferences.mute.get(self.__mixer, False):
        relative_volume = 0.0

      self.__engine.play_sound(filepath, self.__id, mode, relative_volume, fade)

    def stop_sound(self, fade):
      """
      Stops any sound that might be playing.

      Args:
        fade (float): Duration in seconds to fade out.
      """
      self.__active = None
      self.__engine.stop_sound(self.__id, fade)

    def set_sound_volume(self, volume, fade):
      """
      Sets the sound volume level.

      Args:
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade.
      """
      if self.__active is None:
        return

      self.__active['volume'] = volume

      relative_volume = volume * renpy.game.preferences.volumes.get(self.__mixer, 1.0)
      if renpy.game.preferences.mute.get(self.__mixer, False):
        relative_volume = 0.0

      self.__engine.set_sound_volume(self.__id, relative_volume, fade)