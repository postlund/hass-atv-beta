# Apple TV Beta Component

**==> READ EVERYTHING BEFORE UPGRADING!!! <==**

This is the beta version of the Apple TV integration for Home Assistant. Use with
care, possibly unstable and/or non-working code lives here. Be warned (but also, be brave).

Issues and trouble reports should be reported in the `pyatv` repository:

[**>> Report issues here <<**](https://github.com/postlund/pyatv/issues)

## New features

There are a few new features introduced by this integration, currently not in the version
shipped with Home Assistant:

* tvOS 15 support
* HomePods (full media controls)
* Local audio files and HTTP(S) can be streamed via RAOP (AirPlay) to all supported devices
  via the `play_media` service. Make sure `media_type` is set to `music`.
* Basic support for arbitrary AirPlay speakers. Metadata **ONLY** works when streaming
  from Home Assistant, i.e. it will *not* reflect what someone else is streaming to
  the device (the HomePod being an exception). Only `Stop` and `Pause` button works.
* Music app/iTunes in macOS can be controlled
* App launching via `input_source` and media browser (no app icons)
* Support for `volume_set`
* New fields: `media_content_id`, `series_name`, `episode` and `season`

## Changes

## Release 2.2.0

**REQUIRES HOME ASSISTANT 2021.12.x OR LATER!!!**

Updates to pyatv 0.9.8 which brings a few fixes (most relevant here):

* As the power state detection is very unreliable, it is now derived in comibation with
  play state (a device could previously be seen as powered off while playing something).
  If something is playing then the device is considered on.
* Button presses are more reliable and should not be ignore or get "stuck" anymore.
* Pressing the pause button when streaming to an AirPlay device will now stop playback.

Changes have been merged back from Home Assistant, which includes a lot of performance
updates related to device discovery via Zeroconf. Might be notable if you have many
devices.

## Release 2.1.0

**REQUIRES HOME ASSISTANT 2021.12.x OR LATER!!!**

Here comes some new features:

* Support for launching apps! Use `select_source` or the media browser. Only works on
  devices running tvOS and if Companion has been paired. If apps aren't shown, remove
  and add the device again and make sure that the *Companion* protocol is paired.
* Current volume is now available and `volume_set` can be used to set a specific volume.
* The following fields are now available if an app sets them: TV series title, episode
  and season number.
## Release 2.0.0

**REQUIRES HOME ASSISTANT 2021.12.x OR LATER!!!**

Uplift to pyatv 0.9.7 which restores the MRP service internally of pyatv, allowing
migration of existing configuration (for people that have not used this component
before but used the official version shipped with Home Assistant) without having to
remove and add a device again.

Experimental support for audio streaming from HTTP(S) is now supported, but beware
that it is very rudimentary and likely breaks if buffering occurs. It should however
work good enough to support Text-To-Speech, which is now supported without my
previous hack.

This release also fixes a bug that some people reported when pairing the Companion
protocol (`TypeError: 0xc0`).

## Release 1.9.0 (1.9.1)

Pulled in more updates from core (just minor changes). Config entry version has
been reverted back to version 1 after feedback from PR to core. This forces everyone
to remove devices and add them again, should be the last time. The benefit here
is that we maintain backwards compatibility when jumping between Home Assistant
versions. Devices are clearly marked under the Integrations page and everything
can be fixed from frontend (no fiddling with files this time). This is my bad as
I was not aware of how versions are supposed to work, sorry!

The "reconfiguration" option has been removed. No one probably used it.

This version **requires** Home Assistant 2021.11.0 or later.

## Release 1.8(.1)

Same as 1.7 but set to require Home Assistant 2021.11.0 (not yet released) as
previous version causes a lot of problems.

## Release 1.7 (pulled back)

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

Experimental support for Text-To-Speech is included built on top of "Streaming audio"
above, so the same limitations apply.

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
