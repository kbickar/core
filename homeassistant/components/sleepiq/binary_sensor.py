"""Support for SleepIQ sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SLEEPIQ_DATA, SLEEPIQ_STATUS_COORDINATOR

ICON = "mdi:bed"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SleepIQ binary sensor."""
    data = hass.data[DOMAIN][config_entry.entry_id][SLEEPIQ_DATA]
    status_coordinator = hass.data[DOMAIN][config_entry.entry_id][
        SLEEPIQ_STATUS_COORDINATOR
    ]

    entities: list[IsInBedBinarySensor] = []
    for bed in data.beds.values():
        for sleeper in bed.sleepers:
            entities.append(IsInBedBinarySensor(sleeper, bed, status_coordinator))

    async_add_entities(entities)


class IsInBedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Implementation of a SleepIQ presence sensor."""

    def __init__(self, sleeper, bed, status_coordinator):
        """Initialize the sensor."""
        super().__init__(status_coordinator)
        self._unique_id = f"{bed.id}-{sleeper.side}-InBed"
        self._sleeper = sleeper
        self._state = sleeper.in_bed
        self._name = f"SleepNumber {bed.name} {sleeper.name} Is In Bed"
        self._bed = bed

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the status of the sensor."""
        return self._sleeper.in_bed

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the class of this sensor."""
        return BinarySensorDeviceClass.OCCUPANCY

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""

        return DeviceInfo(
            identifiers={(DOMAIN, self._bed.id)},
            connections={(device_registry.CONNECTION_NETWORK_MAC, self._bed.mac_addr)},
            manufacturer="SleepNumber",
            name=self._bed.name,
            model=self._bed.model,
        )

    @property
    def unique_id(self):
        """Return the unique id of the binary sensor."""
        return self._unique_id

    @property
    def should_poll(self):
        """Return the device should not poll for updates."""
        return False
