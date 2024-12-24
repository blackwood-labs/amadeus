# Amadeus

Amadeus is a sound engine for Ren'Py which utilizes the FMOD library to bring
extra functionality and enriched musical capabilities to Ren'Py games.

## How to Install

Check out the [INSTALL.md](INSTALL.md) file for detailed instructions on how to
install Amadeus and use it in your games.

The latest version of Amadeus should work out of the box with FMOD v2.02.

Later versions may require informing Amadeus of the FMOD version:
```renpy
$ amadeus = Amadeus(version=0x00020315) # v2.03.15
```

## Current Features

Currently it provides much of the same basic functionality as the normal Ren'Py
audio engine, but the execution is powered by the FMOD core library. In the
future this will allow for additional features that aren't available in the
normal engine.

FMOD events are also supported, to enable more dynamic and responsive
soundscapes. Events can be loaded, parameters can be set, and the event can be
started, stopped, and you can change the volume. Fades are also supported.

### Register Channels

Up to 32 channels can be registered and associated with existing Ren'Py mixers.

To keep memory usage small, only 8 channel slots are created by default, but
if you need more you can allocate up to 32 slots.

The standard `sound`, `music`, and `voice` channels are automatically registered
by default. You can disable automatic registration if you'd prefer to define
your own channels.

```renpy
python:
  amadeus = Amadeus(channel_limit=32, default_channels=False)

  amadeus.register_channel("sound", "sfx")
  amadeus.register_channel("music", "music")
  amadeus.register_channel("voice", "voice")
```

### Play / Stop

Sounds can be played and stopped on each channel. Starting a new sound on a
channel where an existing sound is playing will stop the previous sound and
start playing the new sound.

when the channel is omitted, the sound will play on the first channel that was
registered. Calling the stop function without a channel will similarly stop the
first channel.

*Note:* Loading files from .rpa files is currently unsupported.

```renpy
python:
  amadeus.play_sound("audio/music.ogg")
  amadeus.play_sound("audio/alternate-music.ogg", channel="music")
  amadeus.play_sound("audio/crash.ogg", channel="sound")

  amadeus.stop_sound(channel="music")
```

### Looping

By default sounds will simply play to the end of their tracks. Sounds can be
set to loop when they are played, at which point they will loop until stopped.

```renpy
python:
  amadeus.play_sound("audio/music.ogg", channel="music", loop=True)
  amadeus.play_sound("audio/crash.ogg", channel="sound")

  amadeus.stop_sound(channel="music")
```

### Adjust Volume

Sounds can be started with a relative volume level, and volume can be adjusted
per channel after the sound has started playing. Adjusting the volume level in
the Preferences menu for a given mixer will affect the volume of all associated
channels. Similarly, muting a mixer will mute all associated channels.

*Note:* Using values larger than 1.0 will increase the volume, but may distort the sound.

```renpy
python:
  amadeus.play_sound("audio/quiet.ogg", volume=0.25)
  amadeus.play_sound("audio/loud.ogg", channel="sound", volume=1.5)

  amadeus.set_sound_volume(0.5)
  amadeus.set_sound_volume(0.5, channel="sound")
```

### Fades

Sounds can fade in and out when started/stopped by defining the fade argument
for the number of seconds the fade should last. The fade will respect any
relative volume defined.

You can also fade volume changes after a sound has started by providing the
fade parameter when adjusting the volume.

Fades can be interrupted by a hard stop at any time.

```renpy
python:
  amadeus.play_sound("audio/music.ogg", volume=0.5, fade=10.0)

  amadeus.set_sound_volume(1.0, fade=3.0)

  amadeus.stop_sound(fade=25.0)

  amadeus.stop_sound()
```

## FMOD Events

Up to 32 events can be loaded and associated with existing Ren'Py mixers.

To keep memory usage small, only 8 event slots are created by default, but
if you need more you can allocate up to 32 slots.

```renpy
python:
  amadeus = Amadeus(event_limit=32)
```

### Loading Banks

FMOD events are contained in files called "Banks", which must be loaded before
the the engine can play the events. It is recommended to load the bank files
during the init phase of your game.

*Note:* No bank files are distributed with Amadeus, but the FMOD download
contains some sample banks, which are referenced in the Amadeus test script.

```renpy
python:
  amadeus.load_bank("amadeus/test_files/Master.bank")
  amadeus.load_bank("amadeus/test_files/Master.strings.bank")
```

### Playing Events

Events must first be loaded before they can be used. Each event can be
associated with a specific Ren'Py mixer, such that the volume of the event will
be affected by the mixer master volume. Attempting to use an event before it is
loaded will result in errors. An event will automatically unload after it has
been stopped, to free up resources. It must be loaded again before it can be
used.

```renpy
python:
  amadeus.load_event("Events/Event-Name", mixer="sfx")

  amadeus.start_event("Events/Event-Name")

  amadeus.stop_event("Events/Event-Name")
```

### Setting Parameters

You can set parameters on FMOD events to modify their behavior. Event parameters
can be set before or after an event has started playing. Attempting to set a
parameter that doesn't exist on a particular event will result in errors.

Be sure to check with your FMOD project to check which parameters are available
for each event.

```renpy
python:
  event = "Events/Event-Name"

  amadeus.load_event(event)
  amadeus.set_event_params(event, {"Some-Param": 2.0})

  amadeus.start_event(event)

  amadeus.set_event_params(event, {"Some-Param": 5.0, "Some-Other-Param": 1.0})

  amadeus.stop_event(event)
```

### Adjust Volume

Just like regular sounds, events can be started with a relative volume level,
which can be adjusted per event after it has started playing. Adjusting the
volume level in the Preferences menu for a given mixer will affect the volume
of all associated events. Similarly, muting a mixer will mute those events.

*Note:* Using values larger than 1.0 will increase the volume, but may distort the sound.

```renpy
python:
  event = "Events/Event-Name"

  amadeus.load_event(event)
  amadeus.start_event(event, volume=0.5)

  amadeus.set_event_volume(event, 1.0)

  amadeus.stop_event(event)
```

### Fades

Event volume adjustments can be set to fade, to allow a smoother transition.

Fades can be interrupted by a hard stop at any time.

```renpy
python:
  event = "Events/Event-Name"

  amadeus.load_event(event)
  amadeus.start_event(event, volume=0.5, fade=10.0)

  amadeus.set_event_volume(event, 1.0, fade=2.0)

  amadeus.stop_event(event, fade=25.0)

  amadeus.stop_event(event)
```

### Ensure Elapsed Time

Certain events may depend on having reached a specific time when a parameter is
adjusted (to advance stages in a multi-stage music piece, for example).

You can ensure that the current event has reached the given timestamp to
accommodate this use-case. If the elapsed time has not yet reached the specified
time, it will jump to the given timestamp. If the event has already passed the
given time, nothing will happen.

```renpy
python:
  event = "Events/Event-Name"

  amadeus.load_event(event)
  amadeus.start_event(event)

  amadeus.ensure_event_time_elapsed(event, 20.0)
  amadeus.set_event_params(event, {"Stage": 2.0})

  amadeus.stop_event(event)
```