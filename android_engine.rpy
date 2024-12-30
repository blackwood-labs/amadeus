init python:

  if renpy.android:
    try:
      import jnius
    except ModuleNotFoundError:
      # Weird environment, maybe running in android mode on a PC?
      # Ignore the import error, and rely on the main init falling back to Core
      pass
    
  class AmadeusAndroidEngine(AmadeusEngine):
    """
    Android engine for Amadeus.
    """

    def __init__(self, channel_limit, event_limit, version):
      """
      Initialize FMOD.

      Args:
        channel_limit (int): The maximum number of channels allowed to be registered.
        event_limit (int): The maximum number of events allowed to be run at once.
        version (int): The version of FMOD loaded via the pre-compiled libraries.
      """
      self.__event_limit = event_limit;

      mainActivity = jnius.autoclass('org.renpy.android.PythonSDLActivity').mActivity
      self.__engine = jnius.autoclass('net.blackwoodlabs.renpy.Amadeus').getInstance()
      self.__engine.init(mainActivity, channel_limit, event_limit, version)

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
      # Assets in Android when packaged via rapt are packed such that we need
      # to prefix each directory and file name with "x-"
      sections = filepath.split('/');
      for i, section in enumerate(sections):
        sections[i] = 'x-' + sections[i]
      filepath = '/'.join(sections)

      # FMOD can find Android assets when prefixed with "file:///android_asset/"
      self.__engine.play_sound('file:///android_asset/x-game/' + filepath, channel_id, mode, volume, fade)

    def is_sound_playing(self, channel_id):
      """
      Checks if a sound on the specified channel is currently playing.

      Args:
        channel_id (int): The numeric ID of the channel to check.

      Returns:
        True if the channel is playing sound, False otherwise.
      """
      return self.__engine.is_sound_playing(channel_id)

    def stop_sound(self, channel_id, fade):
      """
      Stops the sound on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to stop the sound on.
        fade (float): Duration in seconds to fade out.
      """
      self.__engine.stop_sound(channel_id, fade)

    def set_sound_volume(self, channel_id, volume, fade):
      """
      Sets the sound volume on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to set the volume on.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade.

      Raises:
        ValueError: The specified channel does not exist.
      """
      self.__engine.set_sound_volume(channel_id, volume, fade)

    def load_bank(self, filepath):
      """
      Loads a bank file into FMOD Studio.

      Args:
        filepath (str): The path of the bank file to load.
      """
      # Assets in Android when packaged via rapt are packed such that we need
      # to prefix each directory and file name with "x-"
      sections = filepath.split('/');
      for i, section in enumerate(sections):
        sections[i] = 'x-' + sections[i]
      filepath = '/'.join(sections)

      # FMOD can find Android assets when prefixed with "file:///android_asset/"
      self.__engine.load_bank('file:///android_asset/x-game/' + filepath)

    def load_event(self, name, slot_id):
      """
      Loads an event into memory and makes it ready for use.

      Args:
        name (str): The name of the event to load.
        slot_id (int): The event slot to load the event into.
      """
      self.__engine.load_event('event:/' + name, slot_id)

    def is_event_loaded(self, slot_id):
      """
      Checks if the event in the specified slot is currently loaded.

      Args:
        slot_id (int): The event slot to check.

      Returns:
        True if the event is loaded, False otherwise.
      """
      return self.__engine.is_event_loaded(slot_id)

    def set_event_param(self, slot_id, key, value):
      """
      Sets a parameter value on an event.

      Args:
        slot_id (int): The event slot of the event to set the parameter on.
        key (str): The parameter key.
        value (float): The parameter value.
      """
      self.__engine.set_event_param(slot_id, key, value)

    def start_event(self, slot_id, volume, fade):
      """
      Starts an event.

      Args:
        slot_id (int): The event slot of the event to start.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade in.
      """
      self.__engine.start_event(slot_id, volume, fade)

    def stop_event(self, slot_id, fade):
      """
      Stops an event in the given slot.

      Args:
        slot_id (int): The event slot of the event to stop.
        fade (float): Duration in seconds to fade out.
      """
      self.__engine.stop_event(slot_id, fade)

    def set_event_volume(self, slot_id, volume, fade):
      """
      Sets the volume for an event in the given slot.

      Args:
        slot_id (int): The event slot of the event to set the volume for.
        volume (float): Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
        fade (float): Duration in seconds to fade.
      """
      self.__engine.set_event_volume(slot_id, volume, fade)

    def ensure_event_time_elapsed(self, slot_id, time):
      """
      Ensures that the given event has reached the specified time.

      Args:
        slot_id (int): The event slot of the event to check.
        time (float): The number of seconds to ensure have elapsed.
      """
      self.__engine.ensure_event_time_elapsed(slot_id, time)
