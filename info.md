# Apple TV Beta Component

**==> READ EVERYTHING BEFORE UPGRADING!!! <==**

**TL;DR Initial work to support tvOS 15. Old config is not compatible, please remove
previously added devices before upgrading (or let me know what happens if you don't)!**

This is the beta version of the Apple TV integration for Home Assistant. Use with
care, possibly unstable and/or non-working code lives here. Be warned (but also, be brave).

Issues and trouble reports should be reported in the `pyatv` repository:

[**>> Report issues here <<**](https://github.com/postlund/pyatv/issues)

## New features

There are a few new features introduced by this integration, currently not in the version
shipped with Home Assistant:

* tvOS 15 support
* HomePods (full media controls)
* Local audio files can be streamed via RAOP (AirPlay) to all supported devices
  via the `play_media` service
* Basic support for arbitrary AirPlay speakers. Metadata **ONLY** works when streaming
  from Home Assistant, i.e. it will *not* reflect what someone else is streaming to
  the device (the HomePod being an exception). Only `Stop` button works.
* Music app/iTunes in macOS can be controlled

## Changes

## Release 1.8

Same as 1.7 but set to require Home Assistant 2021.11.0 (not yet released) as
previous version causes a lot of problems.

## Release 1.7

This update brings in changes made to core, which is mainly minor code quality
updates but also initial power management support. Calling turn_on or turn_off
will now trigger sleep or wake the device (but only if supported). When sleeping,
the `standby` is reported as state (as that is really what is happening).

**IMPORTANT: State will be wrong (still "on") if you use an external speaker for
output, like a HomePod. This is known and no fix is available for it.**

Bumps to pyatv [0.9.6](https://github.com/postlund/pyatv/releases/tag/v0.9.6)
which is just a minor service release.

## Release 1.6

Amateur hour: fix another error with the TTS change in previous release.

### Release 1.5

Fix error when using TTS.

### Release 1.4

* Lots of work has been done to prevent the same device showing up multiple times in the
  integrations page.
* The pre-fill and "device suggestions" part of manually adding a device have been removed
  to simplify the config flow. Regular Zeroconf discovery should already handle this for
  most people.
* Supported feature flags are now updated in the `media_player`, so only controls actually
  supported will be shown. This is especially convenient for pure AirPlay receivers as
  only `Stop` is supported, but it was not shown as `Pause` overrode that.

### Release 1.3

This release is mainly preparation for what will be included in Home Assistant.
Things that have changed:

* Re-structured the repo a bit to make it easier to develop
* Updated and added test cases
* Bumped pyatv to 0.9.5
* Now using release tags instead of just top commit (HACS)
* A warning will be shown when pairing with a password protected device as that is not supported
* All translations except for english have been dropped

### Release 3

* MRP servive is ignored for tvOS 15 devices which means there should be no
  (failed) attempts to pair that protocol
* Connecting to Apple TV 3 (and older) devices should work again
* Stop is now supported by RAOP, which means it is now possible to stop
  a file that is being streamed

### Release 2

**Config entry version has been bumped with no migration path, please remove all
devices and add them again.**

* All unique identifiers belonging to a device is now stored in the config
  entry and are used during discovery. This should make discovery more reliable
  and hopefully not produce duplicate entries in the Integrations page.
* Music app/iTunes can now be paired properly
* Model name now supports names as raw strings, which allows Home Assistant
  to display the manufacturers model name (you will notice this for
  auto-discovered devices).
* Bug fix for non-working volume controls with grouped devices (MRP)

### Release 1

Summary of changes:

* Restores support for tvOS 15, still rough around the edges
* Supports HomePods (full media controls)
* Local audio files can be streamed via RAOP (AirPlay) to all supported devices
  via the `play_media` service
* Basic support for arbitrary AirPlay speakers. Metadata **ONLY** works when streaming
  from Home Assistant, i.e. it will *not* reflect what someone else is streaming to
  the device (the HomePod being an exception). No media controls are working.
* Barely tested meaning tons of fun testing for you!

Known issues:

* Music app/iTunes instances are discovered, but pairing will fail as pairing Companion
  is not possible (no PIN) - will be fixed in next update

## Setting up

Head over to that Integrations page and add an Apple TV from there. You have to
provide either the name of a device, its IP-address or a unique identifier
(that you got via `atvremote scan`). If everything works as expected you should
see the discovered devices during the initial step.

## Streaming audio

If the RAOP protocol is properly set up during pairing *and* if a file with supported
file type is provided when calling the `play_media` service, then the integration will
now stream that file to the device, which is great. However, no media controls except for
stop works in this case. This is a limitation in pyatv: those features are not supported
*yet*.

**Please do not open issues regarding this!**

## Text-To-Speech

A hack to support TTS is included here. It will likely not be included in the final
merged version of the integration, but hopefully serve as a PoC to show what is needed
to support it. The goal is to come up with a proper way of doing this.

This is built on top of "Streaming audio" above, so the same limitations apply.

**Again, please do not open issues regarding this!**

## Debug logs

If you run into problems, please (please, **please**) make sure you include debug
logs. It is really hard to debug without them. You enable them like this:

```yaml
logger:
  logs:
    pyatv: debug
    custom_components.apple_tv: debug
```

## Finally...

Remember, this is beta software. Features are not fully developed yet, things
will not work, etc. If you try it out, I would be *very* grateful if you reported
any issues you encounter. It helps me iron out bugs and making the integration
stable before submitting it to Home Assistant. It's a win-win in the end, really.
