default AMADEUS_STATE = {}

init python:

  class Amadeus():
    """
    Amadeus sound engine.
    """

    def __init__(self, channel_limit=8, event_limit=8, version=0x00020299, default_channels=True):
      self.__channel_limit = channel_limit
      self.__channel_list = []
      self.__event_limit = event_limit
      self.__event_slots = {}
      self.__banks = []
      self.__version = version
      self.__mixer_volume = {}

      if renpy.android:
        # The FMOD library expects to be loaded via Android JNI
        # It encounters an ill-defined internal error when loading via python CDLL
        # Therefore, we implement a separate engine implementation for Android
        try:
          self.__engine = AmadeusAndroidEngine(channel_limit, event_limit, version)
        except NameError:
          # If the jnius library isn't available, try loading the core engine instead
          self.__engine = AmadeusCoreEngine(channel_limit, event_limit, version)
      else:
        self.__engine = AmadeusCoreEngine(channel_limit, event_limit, version)

      # Register default channels if enabled
      if default_channels:
        self.register_default_channels()

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
        return

      channels = []
      for channel in self.__channel_list:
        data = {
          'id': channel.get_id(),
          'name': channel.get_name(),
          'mixer': channel.get_mixer(),
          'now_playing': channel.now_playing(),
        }
        channels.append(data)

      AMADEUS_STATE['channels'] = channels

      AMADEUS_STATE['event_slots'] = self.__event_slots

    def load(self):
      """
      Load state from the global variable into the engine.

      If there are any active channels, restart playing sound on those channels.
      """
      global AMADEUS_STATE
      if not 'AMADEUS_STATE' in globals():
        return

      load_state = AMADEUS_STATE.copy()

      # Stop all sounds without affecting state
      for channel in self.__channel_list:
        channel.stop_sound(0.0)
      for slot_id in self.__event_slots:
        self.__engine.stop_event(slot_id, 0.0)

      # Restore channels and start playing any active sounds
      self.clear_channels()
      for channel_data in load_state['channels']:
        self.register_channel(channel_data['name'], channel_data['mixer'])
        if channel_data['now_playing'] is not None:
          channel = self.__get_channel(channel_data['name'])
          channel.play_sound(*channel_data['now_playing'].values())

      # Restore event slots and start playing any active events
      for slot_id in load_state['event_slots']:
        event = load_state['event_slots'][slot_id]
        if event is not None and event['save']:
          self.load_event(event['name'], event['mixer'])
          for key in event['parameters'].keys():
            self.set_event_params(event['name'], event['parameters'])
          self.ensure_event_time_elapsed(event['name'], event['position'])
          if event['started']:
            self.start_event(event['name'], event['volume'])

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

      for i in self.__event_slots:
        if not self.__engine.is_event_loaded(i):
          self.__event_slots[i] = None # Stopped at some point, kill it

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

    def get_event_limit(self):
      """
      Accessor to get the event limit.

      Returns:
        The event limit.
      """
      return self.__event_limit

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
        if channel.get_name() == name:
          return

      channel = AmadeusChannel(engine=self.__engine, id=len(self.__channel_list), name=name, mixer=mixer)

      self.__channel_list.append(channel)
      self.save()

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
      self.save()

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

      channel = self.__get_channel(channel)
      channel.stop_sound(0.0)

      channel.play_sound(filepath, loop, volume, fade)
      self.save()

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
      channel.stop_sound(fade)
      self.save()

    def stop_all_sounds(self, fade=0.0):
      """
      Stops sounds on all channels.

      Args:
        fade (float): Duration in seconds to fade out.
      """
      for channel in self.__channel_list:
        channel.stop_sound(fade)

      self.save()

    def set_sound_volume(self, volume, channel=None, fade=0.0):
      """
      Sets the sound volume on the given channel.

      Args:
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        channel (str): The channel to set the volume on (uses first registered channel if None).
        fade (float): Duration in seconds to fade.

      Raises:
        ValueError: The specified channel does not exist.
      """
      channel = self.__get_channel(channel)
      channel.set_sound_volume(volume, fade)
      self.save()

    def load_bank(self, filepath):
      """
      Loads a bank file into FMOD Studio.

      Args:
        filepath (str): The path of the bank file to load.
      """
      if filepath in self.__banks:
        return # Already loaded

      self.__engine.load_bank(filepath)
      self.__banks.append(filepath)

    def load_event(self, name, mixer='music'):
      """
      Loads an event into memory and makes it ready for use.

      Args:
        name (str): The name of the event to load.
        mixer (str): The Ren'Py mixer to associate with the event.
      """
      try:
        event = self.__get_event(name)
        return # Already loaded.
      except ValueError:
        pass # Not loaded, proceed.

      # Try to find an empty slot
      slot_id = None
      for i in self.__event_slots:
        event = self.__event_slots[i]
        if event is None:
          slot_id = i

      # All slots are full, do we have enough space to append?
      if slot_id is None:
        slot_id = len(self.__event_slots.keys())
        if slot_id == self.__event_limit:
          raise RuntimeError('Exceeded maximum number of events')

      self.__engine.load_event(name, slot_id)

      event = {}
      event['slot_id'] = slot_id
      event['name'] = name
      event['mixer'] = mixer
      event['volume'] = 1.0
      event['save'] = True
      event['started'] = False,
      event['parameters'] = {}
      event['position'] = 0.0
      self.__event_slots[slot_id] = event
      self.save()

    def set_event_params(self, event, params):
      """
      Sets parameters on a given event.

      Args:
        event (str): The name of the event to set the parameter on.
        params (dict): The event parameters to set as a dict of key => value.
      """
      event = self.__get_event(event)
      event_params = event['parameters']

      for key in params:
        value = params[key]
        event_params[key] = value
        self.__engine.set_event_param(event['slot_id'], key, value)
      self.save()

    def start_event(self, name, volume=1.0, fade=0.0):
      """
      Starts an event.

      Args:
        name (str): The name of the event to start.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade in.
      """
      event = self.__get_event(name)
      event['volume'] = volume
      event['started'] = True

      relative_volume = volume * self.__get_mixer_volume(event['mixer'])

      self.__engine.start_event(event['slot_id'], relative_volume, fade)
      self.save()

    def stop_event(self, name, fade=0.0):
      """
      Stops an event.

      Args:
        name (str): The name of the event to stop.
        fade (float): Duration in seconds to fade out.
      """
      event = self.__get_event(name)
      event['save'] = False
      self.__engine.stop_event(event['slot_id'], fade)
      if fade == 0.0:
        # Only remove event reference when not fading
        # Allows a later hard stop after starting a fade if needed
        self.__event_slots[event['slot_id']] = None
      self.save()

    def stop_all_events(self, fade=0.0):
      """
      Stops all events.

      Args:
        fade (float): Duration in seconds to fade out.
      """
      for event in self.__event_slots.values():
        if event != None:
          event['save'] = False
          self.__engine.stop_event(event['slot_id'], fade)
          self.__event_slots[event['slot_id']] = None
      self.save()

    def set_event_volume(self, event, volume, fade=0.0):
      """
      Sets the sound volume on the given event.

      Args:
        name (str): The name of the event to set the volume on.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
        fade (float): Duration in seconds to fade.
      """
      event = self.__get_event(event)
      event['volume'] = volume

      relative_volume = volume * self.__get_mixer_volume(event['mixer'])

      self.__engine.set_event_volume(event['slot_id'], relative_volume, fade)
      self.save()

    def ensure_event_time_elapsed(self, event, time):
      """
      Ensures that the given event has reached the specified time.

      This is useful for triggers which rely on specific timing.

      Args:
        event (str): The name of the event to set the elapsed time on.
        time (float): The number of seconds to ensure have elapsed.
      """
      event = self.__get_event(event)
      event['position'] = time

      self.__engine.ensure_event_time_elapsed(event['slot_id'], time)
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
        if channel.get_name() == name:
          return channel

      raise ValueError('Unknown Amadeus channel: ' + str(name))

    def __get_event(self, name):
      """
      Retrieves a given event obj by name.

      Args:
        name (str): The name of the event to return.

      Returns:
        A dict containing the details of the event.

      Raises:
        ValueError: The specified event does not exist.
      """
      for slot_id in self.__event_slots:
        event = self.__event_slots[slot_id]
        if event is not None and event['name'] == name:
          return event

      raise ValueError('Unknown Amadeus event: ' + str(name))

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
      Sets the volume level for all events associated with the specified Ren'Py mixer.

      Args:
        mixer (str): The name of the Ren'Py mixer fetch the volume for.
        volume (float): Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
      """
      for event in self.__event_slots.values():
        if event != None and mixer == event['mixer']:
          self.__engine.set_event_volume(event['slot_id'], volume * event['volume'], 0.0)

    def __sync_mixer_volume(self):
      """
      Synchronize the volume of Ren'Py mixers with all associated events.
      """
      for mixer in renpy.music.get_all_mixers():
        volume = self.__get_mixer_volume(mixer)
        if mixer not in self.__mixer_volume or volume != self.__mixer_volume[mixer]:
          self.__set_mixer_volume(mixer, volume)
          self.__mixer_volume[mixer] = volume
