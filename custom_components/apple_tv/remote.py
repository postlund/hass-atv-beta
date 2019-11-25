"""Remote control support for Apple TV."""
from homeassistant.components import remote

from homeassistant.const import CONF_NAME

from .const import DOMAIN, KEY_API, KEY_POWER, CONF_IDENTIFIER


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Apple TV remote platform."""
    if not discovery_info:
        return

    identifier = discovery_info[CONF_IDENTIFIER]
    name = discovery_info[CONF_NAME]
    api = hass.data[KEY_API][identifier]
    power = hass.data[KEY_POWER][identifier]

    async_add_entities([AppleTVRemote(api, power, name)])


class AppleTVRemote(remote.RemoteDevice):
    """Device that sends commands to an Apple TV."""

    def __init__(self, atv, power, name):
        """Initialize device."""
        self._atv = atv
        self._name = name
        self._power = power
        self._power.listeners.append(self)

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Apple",
            "model": "Remote",
            "name": self.name,
            "sw_version": "0.0",
            "via_device": (DOMAIN, self._atv.metadata.device_id),
        }

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return "remote_" + self._atv.metadata.device_id

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._power.turned_on

    @property
    def should_poll(self):
        """No polling needed for Apple TV."""
        return False

    async def async_turn_on(self, **kwargs):
        """Turn the device on.

        This method is a coroutine.
        """
        await self._power.set_power_on(True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off.

        This method is a coroutine.
        """
        await self._power.set_power_on(False)

    def async_send_command(self, command, **kwargs):
        """Send a command to one device.

        This method must be run in the event loop and returns a coroutine.
        """
        # Send commands in specified order but schedule only one coroutine
        async def _send_commands():
            for single_command in command:
                if not hasattr(self._atv.remote_control, single_command):
                    continue

                await getattr(self._atv.remote_control, single_command)()

        return _send_commands()
