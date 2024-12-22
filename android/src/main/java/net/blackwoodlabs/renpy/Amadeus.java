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

	private native void fmodInit(int channel_limit, int event_limit, int version);
	private native boolean fmodIsEventLoaded(int slot_id);
	private native void fmodShutdown();
	private native void fmodTick();
	private native void fmodPlaySound(String filepath, int channel_id, int mode, float volume, float fade);
	private native void fmodStopSound(int channel_id, float fade);
	private native void fmodSetSoundVolume(int channel_id, float volume, float fade);
	private native void fmodLoadBank(String filepath);
	private native void fmodLoadEvent(String name, int slot_id);
	private native void fmodSetEventParam(int slot_id, String key, float value);
	private native void fmodStartEvent(int slot_id, float volume, float fade);
	private native void fmodStopEvent(int slot_id, float fade);
	private native void fmodSetEventVolume(int slot_id, float volume, float fade);

	/**
	 * Static variable for Singleton pattern
	 */
	private static final Amadeus instance = new Amadeus();

	/**
	 * Private constructor to load the required libraries
	 */
	private Amadeus() {
		System.loadLibrary("fmod");
		System.loadLibrary("fmodstudio");
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
	 * @param event_limit The maximum number of events allowed to be run at once.
	 * @param version The version of FMOD we are loading.
	 */
	public void init(Activity activity, int channel_limit, int event_limit, int version) {
		org.fmod.FMOD.init(activity);

		fmodInit(channel_limit, event_limit, version);
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

	/**
	 * Sets the sound volume on the given channel.
	 *
	 * @param channel_id The numeric ID of the channel to set the volume on.
	 * @param volume Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
	 * @param fade (float): Duration in seconds to fade.
	 */
	public void set_sound_volume(int channel_id, float volume, float fade) {
		fmodSetSoundVolume(channel_id, volume, fade);
	}

	/**
	 * Loads a bank file into FMOD Studio.
	 *
	 * @param filepath The path of the bank file to load.
	 */
	public void load_bank(String filepath) {
		fmodLoadBank(filepath);
	}

	/**
	 * Loads an event into memory and makes it ready for use.
	 *
	 * @param name The name of the event to load.
	 * @param slot_id The event slot to load the event into.
	 */
	public void load_event(String name, int slot_id) {
		fmodLoadEvent(name, slot_id);
	}

	/**
	 * Checks if the event in the specified slot is currently loaded.
	 *
	 * @param slot_id The event slot to check.
	 *
	 * @return True if the event is loaded, False otherwise.
	 */
	public boolean is_event_loaded(int slot_id) {
		return fmodIsEventLoaded(slot_id);
	}

	/**
	 * Sets a parameter value on an event.
	 *
	 * @param slot_id The event slot of the event to set the parameter on.
	 * @param key The parameter key.
	 * @param value The parameter value.
	 */
	public void set_event_param(int slot_id, String key, float value) {
		fmodSetEventParam(slot_id, key, value);
	}

	/**
	 * Starts an event.
	 *
	 * @param slot_id The event slot of the event to start.
	 * @param volume Relative volume percent, where 1.0 = 100% of mixer and 0.0 = 0%.
	 * @param fade Duration in seconds to fade in.
	 */
	public void start_event(int slot_id, float volume, float fade) {
		fmodStartEvent(slot_id, volume, fade);
	}

	/**
	 * Stops an event in the given slot.
	 *
	 * @param slot_id The event slot of the event to stop.
	 * @param fade Duration in seconds to fade out.
	 */
	public void stop_event(int slot_id, float fade) {
		fmodStopEvent(slot_id, fade);
	}

	/**
	 * Sets the volume for an event in the given slot.
	 *
	 * @param slot_id The event slot of the event to set the volume for.
	 * @param volume Relative volume percent, where 1.0 = 100% and 0.0 = 0%.
	 * @param fade Duration in seconds to fade.
	 */
	public void set_event_volume(int slot_id, float volume, float fade) {
		fmodSetEventVolume(slot_id, volume, fade);
	}
}