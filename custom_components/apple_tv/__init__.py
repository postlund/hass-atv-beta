"""The Apple TV integration."""
import asyncio
from functools import partial
import logging
from random import randrange
from typing import Sequence, TypeVar, Union

from pyatv import connect, exceptions, scan
from pyatv.const import Protocol, PowerState
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.media_player import DOMAIN as MP_DOMAIN
from homeassistant.components.remote import DOMAIN as REMOTE_DOMAIN
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_PROTOCOL,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.device_registry as dr

from .const import (
    CONF_CREDENTIALS,
    CONF_CREDENTIALS_AIRPLAY,
    CONF_CREDENTIALS_DMAP,
    CONF_CREDENTIALS_MRP,
    CONF_IDENTIFIER,
    CONF_START_OFF,
    CONF_PWR_MGMT,
    DOMAIN,
    PROTOCOL_DMAP,
    PROTOCOL_MRP,
    SOURCE_INVALID_CREDENTIALS,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Apple TV"

BACKOFF_TIME_UPPER_LIMIT = 300  # Five minutes

NOTIFICATION_TITLE = "Apple TV Notification"
NOTIFICATION_ID = "apple_tv_notification"

SUPPORTED_PLATFORMS = [MP_DOMAIN, REMOTE_DOMAIN]

T = TypeVar("T")  # pylint: disable=invalid-name


# This version of ensure_list interprets an empty dict as no value
def ensure_list(value: Union[T, Sequence[T]]) -> Sequence[T]:
    """Wrap value in list if it is not one."""
    if value is None or (isinstance(value, dict) and not value):
        return []
    return value if isinstance(value, list) else [value]


CREDENTIALS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_CREDENTIALS_MRP): cv.string,
        vol.Optional(CONF_CREDENTIALS_DMAP): cv.string,
        vol.Optional(CONF_CREDENTIALS_AIRPLAY): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_ADDRESS): cv.string,
                        vol.Required(CONF_IDENTIFIER): cv.string,
                        vol.Required(CONF_PROTOCOL): vol.In(
                            [PROTOCOL_DMAP, PROTOCOL_MRP]
                        ),
                        vol.Required(CONF_CREDENTIALS): CREDENTIALS_SCHEMA,
                        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                        vol.Optional(CONF_START_OFF, default=False): cv.boolean,
                        vol.Optional(CONF_PWR_MGMT, default=False): cv.boolean,
                    }
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Apple TV integration."""
    if DOMAIN not in config:
        return True

    for conf in config[DOMAIN]:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=conf,
            )
        )

    return True


async def async_setup_entry(hass, entry):
    """Set up a config entry for Apple TV."""
    manager = AppleTVManager(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.unique_id] = manager

    @callback
    def on_hass_stop(event):
        """Stop push updates when hass stops."""
        asyncio.ensure_future(manager.close_connection(), loop=hass.loop)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)

    for domain in SUPPORTED_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, domain)
        )

    return True


async def async_unload_entry(hass, entry):
    """Unload an Apple TV config entry."""
    manager = hass.data[DOMAIN].pop(entry.unique_id)
    await manager.close_connection()

    for domain in SUPPORTED_PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, domain)

    return True


class AppleTVManager:
    """Connection and power manager for an Apple TV.

    An instance is used per device to share the same power state between
    several platforms. It also manages scanning and connection establishment
    in case of problems.
    """

    def __init__(self, hass, config_entry):
        """Initialize power manager."""
        self.config_entry = config_entry
        self.hass = hass
        self.listeners = []
        self.message = None
        self.atv = None
        self._is_on = not config_entry.options.get(CONF_START_OFF, False)
        self._is_pwr_mgmt_on = config_entry.options.get(CONF_PWR_MGMT, False)
        self._connection_attempts = 0
        self._connection_was_lost = False
        self._task = None
        self.config_entry.add_update_listener(self.async_options_updated)

    async def init(self):
        """Initialize power management."""
        if self._is_on:
            await self.connect()

    def connection_lost(self, exception):
        """Device was unexpectedly disconnected."""
        _LOGGER.warning('Connection lost to Apple TV "%s"', self.atv.name)
        self.atv = None
        self._connection_was_lost = True
        self._update_state(disconnected=True)
        self._start_connect_loop()

    def connection_closed(self):
        """Device connection was (intentionally) closed."""
        self.atv = None
        self._update_state(disconnected=True)
        self._start_connect_loop()

    async def connect(self):
        """Connect to device."""
        if self.atv:
            self._update_state(connected=True)
            if self._is_pwr_mgmt_on:
                _LOGGER.debug("Turning the device on")
                await self.atv.power.turn_on()
        else:
            self._is_on = True
            self._start_connect_loop()

    async def disconnect(self):
        """Turn off device."""
        if self._is_pwr_mgmt_on:
            _LOGGER.debug("Turning the device off")
            await self.atv.power.turn_off()
            self._update_state(disconnected=True)
        else:
            await self.close_connection()

    async def close_connection(self):
        """Disconnect from device."""
        _LOGGER.debug("Disconnecting from device")
        self._is_on = False
        try:
            if self.atv:
                self.atv.push_updater.listener = None
                self.atv.push_updater.stop()
                self.atv.close()
                self.atv = None
            if self._task:
                self._task.cancel()
                self._task = None
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("An error occurred while disconnecting")
        finally:
            self._update_state(disconnected=False)

    def _start_connect_loop(self):
        if not self._task and self.atv is None and self._is_on:
            self._task = asyncio.ensure_future(
                self._connect_loop(), loop=self.hass.loop
            )
        else:
            _LOGGER.debug(
                "Not starting connect loop (%s, %s)", self.atv is None, self._is_on
            )

    async def _connect_loop(self):
        _LOGGER.debug("Starting connect loop")

        # Try to find device and connect as long as the user has said that
        # we are allowed to connect and we are not already connected.
        while self._is_on and self.atv is None:
            try:
                conf = await self._scan()
                if conf:
                    await self._connect(conf)
            except exceptions.AuthenticationError:
                self._auth_problem()
                break
            except asyncio.CancelledError:
                pass
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Failed to connect")
                self.atv = None

            if self.atv is None:
                self._connection_attempts += 1
                backoff = min(
                    randrange(2 ** self._connection_attempts), BACKOFF_TIME_UPPER_LIMIT
                )

                _LOGGER.debug("Reconnecting in %d seconds", backoff)
                await asyncio.sleep(backoff)

        _LOGGER.debug("Connect loop ended")
        self._task = None

    def _auth_problem(self):
        _LOGGER.debug("Authentication error, reconfigure integration")

        name = self.config_entry.data.get(CONF_NAME)
        identifier = self.config_entry.unique_id

        self.hass.components.persistent_notification.create(
            "An irrecoverable connection problem occurred when connecting to "
            "`f{name}`. Please go to the Integrations page and reconfigure it",
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID,
        )

        # Add to event queue as this function is called from a task being
        # cancelled from disconnect
        asyncio.ensure_future(self.close_connection())

        self.hass.async_create_task(
            self.hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_INVALID_CREDENTIALS},
                data={CONF_NAME: name, CONF_IDENTIFIER: identifier},
            )
        )

    async def _scan(self):
        identifier = self.config_entry.unique_id
        address = self.config_entry.data[CONF_ADDRESS]
        protocol = Protocol(self.config_entry.data[CONF_PROTOCOL])

        self._update_state(message="Discovering device...")
        try:
            atvs = await scan(
                self.hass.loop,
                identifier=identifier,
                protocol=protocol,
                hosts=[address],
            )
            if atvs:
                return atvs[0]
        except exceptions.NonLocalSubnetError:
            _LOGGER.debug(
                "Address %s is on non-local subnet, relying on regular scan", address
            )

        _LOGGER.debug(
            "Failed to find device %s with address %s, trying to scan",
            identifier,
            address,
        )

        atvs = await scan(self.hass.loop, identifier=identifier, protocol=protocol)
        if atvs:
            return atvs[0]

        self._update_state("Device not found, trying again later...")
        _LOGGER.debug("Failed to find device %s, trying later", identifier)

        return None

    async def _connect(self, conf):
        credentials = self.config_entry.data[CONF_CREDENTIALS]
        session = async_get_clientsession(self.hass)

        for protocol, creds in credentials.items():
            conf.set_credentials(Protocol(int(protocol)), creds)

        self._update_state("Connecting to device...")
        self.atv = await connect(conf, self.hass.loop, session=session)
        self.atv.listener = self

        self._update_state("Connected, waiting for update...", connected=True)
        self.atv.push_updater.start()

        self.address_updated(str(conf.address))

        await self._setup_device_registry()
        
        if self._is_pwr_mgmt_on:
            self.power_listener = PowerListener(self)
            self.atv.power.listener = self.power_listener
            if self.atv.power.power_state in [PowerState.On, PowerState.Unknown]:
                self._update_state(connected=True)
            else:
                self._update_state(disconnected=True)

        self._connection_attempts = 0
        if self._connection_was_lost:
            _LOGGER.info(
                'Connection was re-established to Apple TV "%s"', self.atv.service.name
            )
            self._connection_was_lost = False

    async def _setup_device_registry(self):
        attrs = {
            "identifiers": {(DOMAIN, self.config_entry.unique_id)},
            "manufacturer": "Apple",
            "name": self.config_entry.data.get(CONF_NAME),
            "model": "Unknown model",
            "sw_version": "Unknown version",
            "via_device": (DOMAIN, self.config_entry.unique_id),
        }

        if self.atv:
            attrs.update(
                {
                    "model": "Apple TV "
                    + self.atv.device_info.model.name.replace("Gen", ""),
                    "sw_version": self.atv.device_info.version,
                }
            )

        device_registry = await dr.async_get_registry(self.hass)
        device_registry.async_get_or_create(
            config_entry_id=self.config_entry.entry_id, **attrs
        )

    @property
    def is_connecting(self):
        """Return true if connection is in progress."""
        return self._task is not None

    def _update_state(self, message="", connected=False, disconnected=False):
        _LOGGER.debug(
            "Updating state: connected=%s, disconnected=%s", connected, disconnected
        )
        for listener in self.listeners:
            if connected:
                listener.device_connected()
            if disconnected:
                listener.device_disconnected()
            self.message = message
            self.hass.async_create_task(listener.async_update_ha_state())

    def address_updated(self, address):
        """Update cached address in config entry."""
        _LOGGER.debug("Changing address to %s", address)
        update_entry = partial(
            self.hass.config_entries.async_update_entry,
            data={**self.config_entry.data, CONF_ADDRESS: address},
        )
        self.hass.add_job(update_entry, self.config_entry)

    @staticmethod
    async def async_options_updated(hass, entry):
        """Triggered by config entry options updates."""
        hass_entry = hass.data[DOMAIN][entry.unique_id]
        hass_entry._is_pwr_mgmt_on = entry.options[CONF_PWR_MGMT]
        if entry.options[CONF_PWR_MGMT] and hass_entry.atv:
            if hass_entry.atv.power.power_state in [PowerState.On, PowerState.Unknown]:
                hass_entry._update_state(connected=True)
            else:
                hass_entry._update_state(disconnected=True)
        else:
            await hass_entry.connect()


class PowerListener:
    """Listener interface for power updates."""

    def __init__(self, manager):
        """Initialize the Apple TV device."""
        self.atv = None
        self._manager = manager

    def powerstate_update(self, old_state, new_state):
        if new_state in [PowerState.On, PowerState.Unknown]:
            self._manager._update_state(connected=True)
        else:
            self._manager._update_state(disconnected=True)

