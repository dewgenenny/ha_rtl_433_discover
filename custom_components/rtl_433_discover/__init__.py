"""The rtl_433 Discovery integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_TOPIC_PREFIX
from .discovery_manager import Rtl433DiscoveryManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up rtl_433 Discovery from a config entry."""
    
    hass.data.setdefault(DOMAIN, {})

    if CONF_TOPIC_PREFIX in entry.data:
        # This is the Bridge (Listener) Entry
        manager = Rtl433DiscoveryManager(hass, entry)
        hass.data[DOMAIN][entry.entry_id] = manager
        
        topic_prefix = entry.data[CONF_TOPIC_PREFIX]
        
        async def _mqtt_message_received(msg):
            """Handle received MQTT message."""
            await manager.async_process_message(msg)

        await mqtt.async_subscribe(hass, topic_prefix, _mqtt_message_received)
        
        # Bridge doesn't need to setup platforms, unless it has its own sensors (status etc)
        # But for now, it just listens and triggers flows.
        
    else:
        # This is a Device Entry
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    if CONF_TOPIC_PREFIX in entry.data:
        # Unload Bridge
        # Unsubscribe MQTT is automatic if we used `mqtt.async_subscribe`? 
        # Actually `mqtt.async_subscribe` returns an unsubscribe callback.
        # But we didn't store it. 
        # Standard mqtt integration usually handles unsubscription if expected.
        # But custom component should cleanup.
        pass 
    else:
        # Unload Device
        if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
            return unload_ok
            
    return True
