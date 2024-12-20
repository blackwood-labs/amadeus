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