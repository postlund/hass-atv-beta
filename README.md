# Apple TV Beta Component

**==> READ EVERYTHING BEFORE UPGRADING!!! <==**

**TL;DR Initial work to support tvOS 15. Old config is not compatible, please remove
previously added devices before upgrading (or let me know what happens if you don't)!**

This is the beta version of the Apple TV integration for Home Assistant. Use with
care, possibly unstable and/or non-working code lives here. Be warned (but also, be brave).

Issues and trouble reports should be reported in the `pyatv` repository:

[**>> Report issues here <<**](https://github.com/postlund/pyatv/issues)

## Changes

### Release 1 (current)

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
now stream that file to the device, which is great. However, no media controls works
in this case. So, you cannot stop, pause or in any way abort something being streamed.
This is a limitation in pyatv: those features are not supported *yet*.

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
