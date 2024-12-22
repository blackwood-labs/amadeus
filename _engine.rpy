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

    @abstractmethod
    def load_bank(self, filepath):
      """
      Loads a bank file into FMOD Studio.

      Args:
        filepath (str): The path of the bank file to load.
      """
      pass

    @abstractmethod
    def load_event(self, name, slot_id):
      """
      Loads an event into memory and makes it ready for use.

      Args:
        name (str): The name of the event to load.
        slot_id (int): The event slot to load the event into.
      """
      pass

    @abstractmethod
    def is_event_loaded(self, slot_id):
      """
      Checks if the event in the specified slot is currently loaded.

      Args:
        slot_id (int): The event slot to check.

      Returns:
        True if the event is loaded, False otherwise.
      """
      pass

    @abstractmethod
    def set_event_param(self, slot_id, key, value):
      """
      Sets a parameter value on an event.

      Args:
        slot_id (int): The event slot of the event to set the parameter on.
        key (str): The parameter key.
        value (float): The parameter value.

      Raises:
        RuntimeError: The given event slot has not been loaded.
      """
      pass

    @abstractmethod
    def start_event(self, slot_id, volume, fade):
      """
      Starts an event.

      Args:
        slot_id (int): The event slot of the event to start.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade in.

      Raises:
        RuntimeError: The given event slot has not been loaded.
      """
      pass

    @abstractmethod
    def stop_event(self, slot_id, fade):
      """
      Stops an event in the given slot.

      Args:
        slot_id (int): The event slot of the event to stop.
        fade (float): Duration in seconds to fade out.
      """
      pass

    @abstractmethod
    def set_event_volume(self, slot_id, volume, fade):
      """
      Sets the volume for an event in the given slot.

      Args:
        slot_id (int): The event slot of the event to set the volume for.
        volume (float): Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
        fade (float): Duration in seconds to fade.

      Raises:
        RuntimeError: The given event slot has not been loaded.
      """
      pass

    @abstractmethod
    def ensure_event_time_elapsed(self, slot_id, time):
      """
      Ensures that the given event has reached the specified time.

      Args:
        slot_id (int): The event slot of the event to check.
        time (float): The number of seconds to ensure have elapsed.

      Raises:
        RuntimeError: The given event slot has not been loaded.
      """
      pass