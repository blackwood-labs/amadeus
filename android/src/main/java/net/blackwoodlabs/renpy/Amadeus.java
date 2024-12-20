package net.blackwoodlabs.renpy;

import android.app.Activity;

/**
 * Android middleware for Amadeus sound engine.
 * 
 * This middleware exists to act as a means to execute library code on the
 * Android platform. Since the python ctypes package isn't on Android, we need
 * an alternate means of communicating with the FMOD libraries. Instead of using
 * ctypes, we can use the pyjnius library to communicate with this middleware, 
 * which in turn uses JNI to communicate with our own C++ code, which can then
 * make calls to the FMOD libraries.
 * 
 * @author Blackwood Labs
 */
public class Amadeus {

	// Native function declarations

	private native void fmodInit(int channel_limit, int version);
	private native void fmodShutdown();
	private native void fmodTick();
	private native void fmodPlaySound(String filepath, int channel_id, int mode, float volume, float fade);
	private native void fmodStopSound(int channel_id, float fade);

	/**
	 * Static variable for Singleton pattern
	 */
	private static final Amadeus instance = new Amadeus();

	/**
	 * Private constructor to load the required libraries
	 */
	private Amadeus() {
		System.loadLibrary("fmod");
		System.loadLibrary("amadeus");
	}

	/**
	 * Singleton accessor
	 *
	 * @return Amadeus middleware singleton instance.
	 */
	public static Amadeus getInstance() {
		return instance;
	}

	/**
	 * Initialize the FMOD library.
	 *
	 * @param activity The Android main activity, used by the Java FMOD library.
	 * @param channel_limit The maximum number of channels allowed to be registered.
	 * @param version The version of FMOD we are loading.
	 */
	public void init(Activity activity, int channel_limit, int version) {
		org.fmod.FMOD.init(activity);

		fmodInit(channel_limit, version);
	}

	/**
	 * Shut down FMOD and release resources.
	 */
	public void shutdown() {
		fmodShutdown();
	}

	/**
	 * Engine tick (20Hz).
	 */
	public void tick() {
		fmodTick();
	}

	/**
	 * Plays sound from the given filepath on a specific channel.
	 *
	 * @param filepath The path of the file to load and play.
     * @param channel_id The numeric ID of the channel to play the sound on.
     * @param mode The mode flags which determine how to play the sound.
     * @param volume Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
     * @param fade Duration in seconds to fade in.
	 */
	public void play_sound(String filepath, int channel_id, int mode, float volume, float fade) {
		fmodPlaySound(filepath, channel_id, mode, fade, volume);
	}

	/**
	 * Stops the sound on the given channel.
	 *
     * @param channel_id The numeric ID of the channel to stop the sound on.
     * @param fade Duration in seconds to fade out.
	 */
	public void stop_sound(int channel_id, float fade) {
		fmodStopSound(channel_id, fade);
	}
}