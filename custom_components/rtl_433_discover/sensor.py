"""Sensor platform for rtl_433 Discovery."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfSpeed,
    UnitOfLength,
    PERCENTAGE,
    LIGHT_LUX,
)

from .const import DOMAIN, SIGNAL_UPDATE_SENSOR
from .discovery_manager import TRACKED_KEYS

_LOGGER = logging.getLogger(__name__)

# Mapping of rtl_433 keys to device classes and units
SENSOR_TYPES = {
    "temperature_C": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "Temperature",
    },
    "humidity": {
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "Humidity",
    },
    "wind_max_m_s": {
        "device_class": SensorDeviceClass.WIND_SPEED,
        "unit": UnitOfSpeed.METERS_PER_SECOND,
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "Wind Max",
    },
    "wind_avg_m_s": {
        "device_class": SensorDeviceClass.WIND_SPEED,
        "unit": UnitOfSpeed.METERS_PER_SECOND,
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "Wind Avg",
    },
    "wind_dir_deg": {
        "device_class": None, 
        "unit": "°",
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "Wind Direction",
    },
    "rain_mm": {
        "device_class": SensorDeviceClass.PRECIPITATION,
        "unit": UnitOfLength.MILLIMETERS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "name": "Rain",
    },
    "light_lux": {
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "unit": LIGHT_LUX,
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "Light",
    },
     "light_klx": {
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "unit": "klx",
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "Light (k)",
    },
    "uv": {
        "device_class": None,
        "unit": "UV",
        "state_class": SensorStateClass.MEASUREMENT,
        "name": "UV Index",
    },
    "battery_ok": {
        "device_class": None,
        "unit": None,
        "state_class": None,
        "name": "Battery OK",
    }
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the rtl_433 sensors for a specific device entry."""
    
    unique_device_id = entry.data["unique_id"]
    model = entry.data["model"]
    
    entities = []
    # Create valid sensors for this device. 
    # For now, since we don't know EXACTLY which fields a device has until we see it,
    # we could just create ALL potential sensors, OR we could rely on the discovery info passed in?
    # BUT, the ConfigEntry data `discovery_info` was static at time of discovery.
    # `rtl_433` devices usually have a fixed set of fields.
    # Let's create sensors for ALL `TRACKED_KEYS` and they will just stay `unavailable` if never updated?
    # OR, better: We only create them if they were in the original discovery payload?
    # Let's check `entry.data` for available keys?
    # For simplicity, let's create what we saw in discovery, OR just all tracked keys.
    # If we create all, it might clutter.
    # If we create only saw, we might miss some that appear later?
    # Usually `rtl_433` sends same set.
    
    # Let's assume we create all tracked keys to be safe and consistent.
    
    for key in TRACKED_KEYS:
        entities.append(Rtl433Sensor(unique_device_id, model, key))
        
    async_add_entities(entities, True)


class Rtl433Sensor(SensorEntity):
    """Representation of a rtl_433 sensor."""

    def __init__(self, unique_device_id, model, key):
        """Initialize the sensor."""
        self._device_id = unique_device_id
        self._model = model
        self._key = key
        
        self._attr_unique_id = f"{unique_device_id}_{key}"
        self._attr_has_entity_name = True
        
        info = SENSOR_TYPES.get(key)
        self._attr_name = info['name'] if info else key.replace("_", " ").title()
        self._attr_device_class = info.get('device_class') if info else None
        self._attr_native_unit_of_measurement = info.get('unit') if info else None
        self._attr_state_class = info.get('state_class') if info else None
        
        self._state = None
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"{self._model} {self._device_id.split('-')[-1]}",
            manufacturer="rtl_433",
            model=self._model,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        unique_sensor_id = f"{self._device_id}_{self._key}"
        signal = f"{SIGNAL_UPDATE_SENSOR}_{unique_sensor_id}"
        
        @callback
        def async_update_state(value):
            """Update the state."""
            self._state = value
            self.async_write_ha_state()
            
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal, async_update_state)
        )
