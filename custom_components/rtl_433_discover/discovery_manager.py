"""Device discovery logic."""
import json
import logging
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN, SIGNAL_NEW_SENSOR, SIGNAL_UPDATE_SENSOR, CONF_IGNORE_DEVICES

_LOGGER = logging.getLogger(__name__)

# List of keys we want to track as sensors
TRACKED_KEYS = [
    "temperature_C",
    "humidity",
    "wind_max_m_s",
    "wind_avg_m_s",
    "wind_dir_deg",
    "rain_mm",
    "light_klx",
    "light_lux",
    "uv",
    "battery_ok"
]

class Rtl433DiscoveryManager:
    """Class to manage rtl_433 discovery."""

    def __init__(self, hass, entry):
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.known_sensors = set() # Store unique_id of sensors we've already created

    @property
    def ignored_devices(self):
        """Return list of ignored devices."""
        ignore_str = self.entry.options.get(CONF_IGNORE_DEVICES, "")
        if not ignore_str:
            return []
        # Split by comma and strip whitespace
        return [x.strip() for x in ignore_str.split(",") if x.strip()]

    async def async_process_message(self, msg):
        """Process a message."""
        try:
            payload = json.loads(msg.payload)
        except json.JSONDecodeError:
            _LOGGER.debug("Failed to decode JSON from %s", msg.topic)
            return

        # Basic validation
        if not isinstance(payload, dict):
            return
            
        model = payload.get("model")
        device_id = payload.get("id")

        if not model or device_id is None:
            # Some devices might not have 'id', but usually they do in rtl_433. 
            # If no ID, we can't really track it reliably as a unique device.
            return

        # Check against Ignore List
        # We check both exact "43951" and "Bresser-7in1-43951" mostly just ID is easier for user
        # But ID might not be unique across models. 
        # Let's support verifying against "model-id" and just "id"
        unique_device_id = f"{model}-{device_id}"
        
        ignored = self.ignored_devices
        # Check explicit unique ID match or simple ID match (converted to string)
        if unique_device_id in ignored or str(device_id) in ignored:
            _LOGGER.debug("Ignoring device %s (matched ignore list)", unique_device_id)
            return

        # Check if already configured
        # We check if a Config Entry exists with this unique_id
        entry = self.hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, unique_device_id)
        
        if entry:
            # Already configured, just update sensors
            # Iterate through payload and update sensors
            for key, value in payload.items():
                if key in TRACKED_KEYS:
                     unique_sensor_id = f"{unique_device_id}_{key}"
                     async_dispatcher_send(self.hass, f"{SIGNAL_UPDATE_SENSOR}_{unique_sensor_id}", value)
        else:
            # Not configured, trigger discovery flow
            discovery_info = {
                "unique_id": unique_device_id,
                "model": model,
                "identifiers": [DOMAIN, unique_device_id], # Pass as list
            }
            # We add all payload data to discovery info so we can use it if needed, 
            # though usually we only need model/id to create the entry.
            # But the entry data usually needs to look like what the device entry expects.
            # Wait, the device entry just needs model/id to start.
            
            # We trigger the flow. This will match against active flows by unique_id automatically.
            await self.hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "discovery"}, 
                data=discovery_info
            )

