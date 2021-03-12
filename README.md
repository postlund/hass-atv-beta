# Apple TV Beta Component

**TL;DR: What you see here is already available in the official Home Assistant releases.
You do not need to use this repository anymore. If you have problems after migrating,
please remove your devices and add them again.**

This is the beta component repository for the Apple TV component in Home Assistant.
In the past, it has been used to ship an upcoming uplift of the Apple TV component
supporting devices running tvOS. That uplift shipped with Home Assistant 2020.12.1.
The repository is kept only for potential major changes in the future, but will for
most part just replicate whatever has already been merged in Home Assistant core
repository. So generally you do not need to use this custom repository at all, unless
instructed to do so for beta testing purposes.

Issues and trouble reports should be reported in the `pyatv` repository:

[**>> Report issues here <<**](https://github.com/postlund/pyatv/issues)

## Changes

### Release 2 (current)

Synchronize with Home Assistant dev branch. Includes support for suggested areas and
bug fix for crashing apps on tvOS 14.5 (beta).

### Release 1

Currently the same as Home Assistant 2021.3.1. Compared to previous version of the
beta component, YAML support has been dropped and some status messages that used to
appear as `title` in the media player has been removed. Some additonal features,
like shuffle, repeat and volume controls have been added. But otherwise it's the same.

It should be safe to upgrade, but if you run in to problems, make sure to remove your
devices from Integrations and adding them again before opening an issue.

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
