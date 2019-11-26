# Apple TV Beta Component

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

* The component will not handle re-connects properly. So if the connection is
  lost, e.g. due to reboots, it will probably not recover until you restart
  Home Assistant. Fixing this is next on the list.

* Using YAML is not supported now, but will be added in the future.

* Already stated in the feature list, but artwork does not work and appears to be
  a bit tricky to fix. We'll see when that happens.

* When pairing with an Apple TV running tvOS, the initial screen with a PIN code
  will not disappear after pairing (so it appears that you get three PIN input
  screens). This is a known issue and is fixed on the `master` branch in `pyatv`.
  It will be integrated into this component soon. For now, you can just ignore
  that screen (e.g. press menu on the remote).

### Changes in this commit

Fixes this problem:

```python
AttributeError: 'Credentials' object has no attribute 'split'
```

In case of problems, remove the Apple TV entity and re-pair.

## Installing

I recommend that you install [HACS](https://hacs.xyz/) and add this repository
to it. That way you get updates automatically. But you can just copy and add
files the old fashined way as well.

## Setting up

Head over to that Integrations page and add an Apple TV from there. You have to
provide either the name of a device, its IP-address or a unique identifier
(that you got via `atvremote scan`). If you are unsure about what to enter, just
type something, press submit and suggestions will be presented for you.

## Debug logs

If you run into problems, please (please, **please**) make sure you include debug
logs. It is really hard to debug without them. You enable them like this:

```yaml
logger:
  logs:
    pyatv: debug
```

## Finally...

Remember, this is beta software. Features are not fully developed yet, things
will not work, etc. If you try it out, I would be *very* grateful if you reported
any issues you encounter. It helps me iron out bugs and making the integration
stable before submitting it to Home Assistant. It's a win-win in the end, really.