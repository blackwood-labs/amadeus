# Installing Amadeus

This document will detail how to install Amadeus and get it working in your games.

## Ren'Py Code Installation

Copy all files and folders in this directory into a new directory called
"amadeus" in your project's "game" directory. 

You can delete the "test.rpy" file and the "test_files" directory, as these are
not needed to use Amadeus in your game. These files won't cause any problems,
but they will take up extra space if you don't delete them.

Please keep the LICENSE.md file in this directory included in your game.

## FMOD Libraries

Amadeus requires the FMOD libraries to run. These libraries are not distributed
with Amadeus, and you'll need register and download them yourself: https://www.fmod.com/download

On the Download page, select FMOD Engine and download the Windows, Mac, Linux,
and packages. If you plan to make an Android build of your game, grab the
Android download as well.

In each download, find the following files and copy them into the
"game/amadeus/lib" directory in your project:

 - Windows: api/core/lib/x64/fmod.dll
 - Linux: api/core/lib/x64/libfmod.so
 - Mac: api/core/lib/x64/libfmod.dylib

Amadeus should now work correctly on PC and Mac OS.

## Android Libraries

There are a few extra steps to accommodate Android builds, which involve making
changes in the Ren'Py rapt tool configuration.

First, copy the FMOD libraries from the Android download into the following
directory in your project "game/amadeus/android/src/main/libfmod":
 - api/core/lib/arm64-v8a/libfmod.so -> libfmod/arm64-v8a/libfmod.so
 - api/core/lib/armeabi-v7a/libfmod.so -> libfmod/armeabi-v7a/libfmod.so
 - api/core/lib/x86/libfmod.so -> libfmod/x86/libfmod.so
 - api/core/lib/x86_64/libfmod.so -> libfmod/x86_64/libfmod.so
 - api/core/lib/fmod.jar -> libfmod/fmod.jar

Next, copy everything in the "game/amadeus/android" directory into the rapt
android directory: "/path/to/renpy-sdk/rapt/project/renpyandroid". This will
override the existing build.gradle file.

Your next Android build will take a bit longer as it downloads and installs a
few extra tools and builds the Amadeus Android libraries for the first time.
Subsequent builds will be considerably faster.