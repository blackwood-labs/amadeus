"""
Tests for the Amadeus sound engine.

These tests are designed to walk through the various pieces of functionality
the engine can provide, and ensures everything is working correctly.
"""
init:
  $ amadeus = Amadeus()

  python:
    def test_suite_reset():
      amadeus.stop_sound(channel="music")
      amadeus.stop_sound(channel="sound")
      amadeus.stop_sound(channel="voice")
      renpy.say(None, '[[INFO] Environment Reset...')

label amadeus_tests:
  image test_suite = "#000"
  scene test_suite

  """
  == BEGIN AMADEUS TEST SUITE ==

  Registering channels...
  """

  $ amadeus.register_channel("music", "music")
  $ amadeus.register_channel("sound", "sfx")
  $ amadeus.register_channel("voice", "voice")

  # Duplicate channel registrations are fine, and are ignored...
  $ amadeus.register_channel("music", "music")

  # Test that invalid mixer causes a ValueError
  python:
    try:
      amadeus.register_channel("invalid", "invalid")
      raise RuntimeError("Failed test...")
    except ValueError:
      pass

  # Test that too many channels causes a RuntimeError
  python:
    orig_channels = amadeus.get_channels()
    try:
      for x in range(0, amadeus.get_channel_limit()):
        amadeus.register_channel(x, "music")
      raise RuntimeError("Failed test...")
    except RuntimeError:
      pass
    amadeus.clear_channels()
    for channel in orig_channels:
      amadeus.register_channel(channel['name'], channel['mixer'])

  """
  Registering channels...{fast} Done!
  """

  """
  Test - Playing missing sound file causes error...
  """

  python:
    try:
      amadeus.play_sound("amadeus/test_files/missing.ogg")
      raise RuntimeError("Failed test...")
    except ValueError:
      pass

  """
  Test - Playing missing sound file causes error...{fast} Success!
  """

  """
  Test - Playing sound on invalid channel causes error...
  """

  python:
    try:
      amadeus.play_sound("amadeus/test_files/ping.ogg", channel="invalid")
      raise RuntimeError("Failed test...")
    except ValueError:
      pass

  """
  Test - Playing sound on invalid channel causes error...{fast} Success!
  """

  """
  Test - Play single sound file in the default channel...
  """

  $ amadeus.play_sound("amadeus/test_files/ping.ogg")

  """
  Test - Play single sound file in the default channel...{fast} Success!
  """

  $ test_suite_reset()

  """
  Test - Play looping sound until stopped...
  """

  $ amadeus.play_sound("amadeus/test_files/ping.ogg", loop=True)

  """
  Test - Play looping sound until stopped...{fast} Success!
  """

  $ test_suite_reset()

  """
  Test - Play sample sound at a lower volume...
  """

  $ amadeus.play_sound("amadeus/test_files/ping.ogg", volume=0.25)

  """
  Test - Play sample sound at a lower volume...{fast} Success!
  """

  $ test_suite_reset()

  """
  Test - Play multiple sounds via different channels...
  """

  $ amadeus.play_sound("amadeus/test_files/beep.ogg", channel="music", loop=True)
  $ amadeus.play_sound("amadeus/test_files/ping.ogg", channel="sound", loop=True)

  """
  Test - Play multiple sounds via different channels...{fast} Success!
  """

  $ test_suite_reset()

  """
  Test - Play sound with fade in...
  """

  $ amadeus.play_sound("amadeus/test_files/loop.ogg", loop=True, fade=5.0)

  """
  Test - Play sound with fade in...{fast} and fade out...
  """

  $ amadeus.stop_sound(fade=5.0)

  """
  Test - Play sound with fade in... and fade out...{fast} Success!
  """

  $ test_suite_reset()

  """
  == AMADEUS TEST SUITE COMPLETE ==
  """

  return
