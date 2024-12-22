init python:

  from abc import ABC, abstractmethod

  class AmadeusEngine(ABC):
    """
    Amadeus engine interface.
    """

    @abstractmethod
    def shutdown(self):
      """
      Shut down the engine to free allocated resources.
      """
      pass

    @abstractmethod
    def tick(self):
      """
      Engine tick (20Hz).
      """
      pass

    @abstractmethod
    def play_sound(self, filepath, channel_id, mode, volume, fade):
      """
      Plays sound from the given filepath on a specific channel.

      Args:
        filepath (str): The path of the file to load and play.
        channel_id (int): The numeric ID of the channel to play the sound on.
        mode (int): The mode flags which determine how to play the sound.
        volume (float): Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
        fade (float): Duration in seconds to fade in.
      """
      pass

    @abstractmethod
    def stop_sound(self, channel_id, fade):
      """
      Stops the sound on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to stop the sound on.
        fade (float): Duration in seconds to fade out.
      """
      pass

    @abstractmethod
    def set_sound_volume(self, channel_id, volume, fade):
      """
      Sets the sound volume on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to set the volume on.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade.
      """
      pass