# Apple TV Beta Component

**TL;DR** If you try this component, read the changelog below to know what has
changed and what to test! Instructions on how to enable debug logs are at the end.

In tvOS 13, Apple dropped their old legacy protocols inherited from iTunes
(DAAP/DACP/DMAP) and now rely fully on their new protocol, Media Remote Protocol.
Or MRP for short. This broke the Apple TV component in Home Assistant as
`pyatv`, the underlying protocol, only supports the old legacy protocol stack.

I have put a lot of work into completing suport for MRP in `pyatv` and it is
starting to reach a point where it is usable. But there is still some work
left until it can be released and all changes integrated back into Home Assistant.
However, I want to give everyone a chance to try out the new component and come
with feedback, so I publish what will become the official component (that is
bundled with Home Assistant by default) here as a custom component so you can
try it out.

Issues and trouble reports should be reported in the `pyatv` repository:

[**>> Report issues here <<**](https://github.com/postlund/pyatv/issues)

## Features and limitations

Currently Home Assistant implements all features that `pyatv` suports for DMAP.
The intention is to implement the same features for MRP first and add additional
features after that. The feature list is available
[here](https://postlund.github.io/pyatv/).

Other limitations as follows:

* As Home Assistant does not support zeroconf for custom components, auto-discovery
  will not work with this component. You will have to manually add your device
  via the Integrations page.

* This component will completely override the builtin component!

### Changes

## pyatv 0.6.1

Fixes this issue:

    AttributeError: 'EnumTypeWrapper' object has no attribute 'NoError'

This happens because some integrations restrict protobuf to a very old version that
pyatv seemed to have lost compatibility with (which is now fixed).

## pyatv 0.6.0

Here comes a few new features:

* Only one Apple TV device is set up in the device registry and it is populated with
  correct device model and OS version (if that could be determined)
* Genre, artist and album attributes will be present if available
* Application name and identifier of active app is now supported
* Some timeouts have been increased as well some mechanisms added to wake sleeping devices,
  which should make scanning and re-connections work better

The application name is not always present (identifier is though) and it is a known issue.
For some reason the application name is not always sent by the Apple TV, so some kind of
workaround to deal with this must figured out. **You do not need to write any issues
about this.**

## pyatv 0.5.0 update 4

Make removal of integration work. Previously the media_player entity would be a leftover
until next restart of Home Assistant.

## pyatv 0.5.0 update 3

Only a few new debug logs were added to aid troubleshooting.

## pyatv 0.5.0 update 2

This updates fixes some review comments regarding usage of `unique_id` in config entries.
A side-effect of this is that that I had to change the config entry format, so you yet
again have to remove and re-pair your devices. This is my bad as I didn't really understand
the concept at first (but I do now), so I didn't think it would have any impact.

Also, the option flow (used to enable "start off" mode) broke some time ago and that has
been fixed. The test for this has been improved so this won't happen again.

I hope this should also fix a few problems when the integration fails to re-establish a
connection and potentially mix up devices (also related to `unique_id`).

### pyatv 0.5.0

This update fixes:

`MessageToString() got an unexpected keyword argument 'print_unknown_fields' `

You will only get this error if you are using another integration depending on
protobuf, e.g. tensor flow or esphome.

This is also a major version bump and comes with various under-the-hood improvements,
see pyatv changelog for details.

### pyatv 0.4.0a16 update 2

Fix this bug introduced in last release:

`NameError: name 'discovery' is not defined`

Contains cosmetic changs after following the Home Assistant checklist.

### pyatv 0.4.0a16

Fixes incorrect position for MRP. Otherwise mostly minor translation updates and code clean ups.

**This will be the base version used for inclusion in Home Assistant.**

#### pyatv 0.4.0

This is the version that will be included in Home Assistant soon. It contains a lot of
fixes to review comments and also fixes this issue:

  TypeError: 'mappingproxy' object does not support item assignment

which is present in 0.107 and later. Also, config entry unloading works now so integrations
can be removed properly.

#### pyatv 0.4.0a15

Minor bug fixes for MRP device states. Seeking state is also implemented for MRP.

Fixed re-connect bug, missing translation when AirPlay would not pair and invalid logging
point.

#### pyatv 0.4.0a14

More improvements to config flow, mainly clearer instructions. Only devices that haven't
already been added to Home Assistant will be shown in the initial dialog. IP-address of
the first found device will be pre-filled to speed up the process.

A lot of improvements have also been made to logging. Some additional log points have
been added to simplify debugging. Log lines are also cropped to not flood the log file.

This error has been fixed (introduced in Home Assistant 0.105.0):

```
2020-02-10 16:11:56 ERROR (MainThread) [homeassistant.helpers.service] Service XXX for YYY
incorrectly returns a coroutine object. Await result instead in service handler. Report bug
to integration author.
```

Lots of tests have been added for the config flow, which revealed a few bugs (mainly
related to DMAP pairing) which has been fixed.

Exponential backoff upper limit was lowered to five minutes for faster feedback.

#### pyatv 0.4.0a13

This release squashes a few metadata bugs (e.g. wrong device state and position).
Artwork is cached (by pyatv) and artwork_id is used to minimize the amount of times
artwork is requested. This should put less strain on Home Assistant.

Previously AirPlay was handled as a special case by `pyatv`, as an implicit service
would be created if one wasn't provided. This would break the integration in case
AirPlay was disabled on device as pairing would still be requested but not possible
to complete. No request will be made now if AirPlay is not available now.

Also some minor improvement and fixes to config flow. One being that an empty
"abort" dialog would be shown due to missing translation.

#### pyatv 0.4.0a12

This release comes with some additional polish in the config flow. An additional
scan is done before the first dialog is shown, so you will get a list of available
devices immediately.

Initial support for reconfiguring a device in case credentials are invalid. This
should never happen, but if authentication fails it will now be possible to pair
again without having to remove and add the integration. Not all cases are caught
yet, so it is not perfect. Will improve this in the next release. A persistent
notification is shown if this happens. To try it out, open `.store/core.config_entries`
and modify for instance MRP credentials to be incorrect and restart Home Assistant.

Exponential backoff is used when reconnecting with an upper limit of 10 minutes.
This will make sure that Home Assistant doesn't hammer too much.

It is now possible to setup a device via yaml (experimental as well):

```yaml
apple_tv:
  - address: 10.0.0.1
    identifier: <id>
    name: Living Room
    protocol: MRP
    credentials:
      mrp: <creds>
      airplay: <creds>
      dmap: <creds>
```

This will create a config entry, unless it doesn't already exist (in case nothing
happens).

Should also fix this error:

    RuntimeError: Session is closed

#### pyatv 0.4.0a11

Support for unicast scanning. If you have problems finding your device, enter its
IP-address (instead of name or identifier) and it should work better.

Minor bug fixes and code improvements. Idle state should be reported better now
instead of paused.

#### pyatv 0.4.0a10

Finally support for artwork!

Improvements to AirPlay to make it more reliable. Should hopefully fix #313.

#### pyatv 0.4.0a9

This is a small fix that makes idle state work for MRP (a device was never
shown as idle before).

#### pyatv 0.4.0a8

Fixes this issue:

    TypeError: Object of type MrpService is not JSON serializable

Remove your integration and add it again and it should work.

Leading zeros in PIN when pairing with AirPlay should work now. (#307)

#### pystv 0.4.0a7

_Beware: this release might be a bit buggy, please help me hunt the bugs down._

Fixes problems with leading zeros in MRP pairing:

https://github.com/postlund/pyatv/issues/291

Hopefully AirPlay streaming works as expected now (please try):

https://github.com/postlund/pyatv/issues/266

Re-connect logic is in place, so re-connections are made automatically.
Might be a bit spammy, will change that later.

Turn on and off should work now. Please note that this *only* means that
"turn off" disconnects from the device so it appears as off in Home Assistant.
It does **not** turn off your Apple TV.

I added the "start off" option as well. You can configure it via Options
by selecting your Apple TV from the Integrations page.

#### pyatv 0.4.0a6

Fixes this problem:

```python
packages/pyatv/mrp/pairing.py", line 32, in close await self.connection.close() TypeError: object NoneType can't be used in 'await' expression
```

#### pyatv 0.4.0a5

Fixes this problem:

```python
AttributeError: 'Credentials' object has no attribute 'split'
```

In case of problems, remove the Apple TV entity and re-pair.

## Installing

I recommend that you install [HACS](https://hacs.xyz/) and add this repository
to it. That way you get updates automatically. But you can just copy and add
files the old fashined way as well.

1. When inside of HACS, go to the "Settings" tab and then you'll see an 
"Add Custom Repository" field at the bottom of that page.
2. Paste in the following URL: https://github.com/postlund/hass-atv-beta and select
Integration" from the Category dropdown and hit the save button.
3. Install it through HACS, this will require a restart of Home Assistant to fully install
After this is done, you can set it up via Home Assistant Configuration -> Integrations page.

## Setting up

Head over to that Integrations page and add an Apple TV from there. You have to
provide either the name of a device, its IP-address or a unique identifier
(that you got via `atvremote scan`). If everything works as expected you should
see the discovered devices during the initial step.

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
