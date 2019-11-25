"""The Apple TV integration."""
import logging

import voluptuous as vol

from homeassistant.core import callback
from homeassistant.helpers import discovery
from homeassistant.const import (
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP,
)

from .const import (
    DOMAIN, CONF_IDENTIFIER, CONF_PROTOCOL, CONF_CREDENTIALS,
    APPLE_TV_DEVICE_TYPES, KEY_API, KEY_POWER
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Set up the Apple TV integration."""
    return True


async def async_setup_entry(hass, entry):
    """Set up a config entry for Apple TV."""
    import pyatv

    identifier = entry.data[CONF_IDENTIFIER]
    protocol = entry.data[CONF_PROTOCOL]
    credentials = entry.data[CONF_CREDENTIALS]
    atvs = await pyatv.scan(hass.loop, identifier=identifier, protocol=protocol)
    if not atvs:
        _LOGGER.error("Failed to find device with identifier " + identifier)
        return False

    conf = atvs[0]
    for protocol, credentials in credentials.items():
        conf.set_credentials(int(protocol), credentials)

    atv = await pyatv.connect(conf, hass.loop)
    power = AppleTVPowerManager(hass, atv, False)

    @callback
    def on_hass_stop(event):
        """Stop push updates when hass stops."""
        atv.push_updater.stop()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)

    hass.data.setdefault(KEY_API, {})[identifier] = atv
    hass.data.setdefault(KEY_POWER, {})[identifier] = power

    dev_reg = await hass.helpers.device_registry.async_get_registry()
    dev_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections=set(),
        identifiers={(DOMAIN, entry.data[CONF_IDENTIFIER])},
        manufacturer="Apple",
        name="Apple TV",
        # model='',
        # sw_version=''
    )

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "media_player")
    )

    hass.async_create_task(
        discovery.async_load_platform(hass, "remote", DOMAIN, entry.data, entry.data)
    )

    return True


class AppleTVPowerManager:
    """Manager for global power management of an Apple TV.

    An instance is used per device to share the same power state between
    several platforms.
    """

    def __init__(self, hass, atv, is_off):
        """Initialize power manager."""
        self.hass = hass
        self.atv = atv
        self.listeners = []
        self._is_on = not is_off

    async def init(self):
        """Initialize power management."""
        if self._is_on:
            self.atv.push_updater.start()
            await self.atv.connect()

    @property
    def turned_on(self):
        """Return true if device is on or off."""
        return self._is_on

    async def set_power_on(self, value):
        """Change if a device is on or off."""
        if value != self._is_on:
            self._is_on = value
            if not self._is_on:
                self.atv.push_updater.stop()
            else:
                self.atv.push_updater.start()
                await self.atv.connect()

            for listener in self.listeners:
                self.hass.async_create_task(listener.async_update_ha_state())
