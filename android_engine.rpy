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

    def __init__(self, channel_limit, version):
      """
      Initialize FMOD.

      Args:
        channel_limit (int): The maximum number of channels allowed to be registered.
        version (int): The version of FMOD loaded via the pre-compiled libraries.
      """
      mainActivity = jnius.autoclass('org.renpy.android.PythonSDLActivity').mActivity
      self.__engine = jnius.autoclass('net.blackwoodlabs.renpy.Amadeus').getInstance()
      self.__engine.init(mainActivity, channel_limit, version)

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

    def stop_sound(self, channel_id, fade):
      """
      Stops the sound on the given channel.

      Args:
        channel_id (int): The numberic ID of the channel to stop the sound on.
        fade (float): Duration in seconds to fade out.
      """
      self.__engine.stop_sound(channel_id, fade)