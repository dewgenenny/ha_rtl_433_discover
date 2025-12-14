"""Test the rtl_433 Discovery logic."""
import json
from unittest.mock import MagicMock, patch
import pytest

from homeassistant.core import HomeAssistant
from custom_components.rtl_433_discover import DOMAIN
from custom_components.rtl_433_discover.discovery_manager import Rtl433DiscoveryManager
from custom_components.rtl_433_discover.const import CONF_IGNORE_DEVICES

SAMPLE_PAYLOAD = """
{"time":"2025-12-14 13:28:51","model":"Bresser-7in1","id":43951,"temperature_C":14.3,"humidity":76,"wind_max_m_s":3.9,"wind_avg_m_s":3.8,"wind_dir_deg":54,"rain_mm":0,"light_klx":14.135,"light_lux":14135.0,"uv":0.6,"battery_ok":1,"mic":"CRC"}
"""

async def test_parsing_and_discovery(hass: HomeAssistant) -> None:
    """Test parsing and discovery."""
    
    # Mock config entry
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.options = {}
    
    manager = Rtl433DiscoveryManager(hass, mock_entry)
    
    # Mock MQTT message
    msg = MagicMock()
    msg.payload = SAMPLE_PAYLOAD
    msg.topic = "rtl_433/events"
    
    # We need to capture dispatch signals or check device registry
    # Since we use async_dispatcher_send, we can mock it or subscribe?
    # Subscribing is better integration test, but mocking is easier unit test.
    # Let's mock device registry
    
    with patch("custom_components.rtl_433_discover.discovery_manager.dr.async_get") as mock_dr_get, \
         patch("custom_components.rtl_433_discover.discovery_manager.async_dispatcher_send") as mock_dispatch:
             
        mock_registry = MagicMock()
        mock_dr_get.return_value = mock_registry
        
        await manager.async_process_message(msg)
        
        # Verify Device Registry called
        assert mock_registry.async_get_or_create.called
        call_args = mock_registry.async_get_or_create.call_args[1]
        assert call_args["identifiers"] == {(DOMAIN, "Bresser-7in1-43951")}
        assert call_args["model"] == "Bresser-7in1"
        
        # Verify Dispatcher called for each sensor
        # 10 keys: temperature_C, humidity, wind x3, rain, light x2, uv, battery
        # Check temperature
        expected_call_temp = ({
            "unique_id": "Bresser-7in1-43951",
            "model": "Bresser-7in1",
            "key": "temperature_C",
            "value": 14.3
        },)
        
        # Verify at least one call matches
        found = False
        for call in mock_dispatch.call_args_list:
            if call[0][1] == expected_call_temp[0]:
                found = True
                break
        assert found, "Temperature sensor dispatch not found"

async def test_ignore_logic(hass: HomeAssistant) -> None:
    """Test ignore logic."""
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.options = {CONF_IGNORE_DEVICES: "Bresser-7in1-43951, 99999"}
    
    manager = Rtl433DiscoveryManager(hass, mock_entry)
    
    msg = MagicMock()
    msg.payload = SAMPLE_PAYLOAD
    msg.topic = "rtl_433/events"
    
    with patch("custom_components.rtl_433_discover.discovery_manager.dr.async_get") as mock_dr_get, \
         patch("custom_components.rtl_433_discover.discovery_manager.async_dispatcher_send") as mock_dispatch:
             
        await manager.async_process_message(msg)
        
        # Should be ignored, so no registry, no dispatch
        assert not mock_dr_get.called
        assert not mock_dispatch.called

async def test_ignore_logic_by_id_only(hass: HomeAssistant) -> None:
    """Test ignore logic by simple ID."""
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.options = {CONF_IGNORE_DEVICES: "43951"} # Simple ID present in payload
    
    manager = Rtl433DiscoveryManager(hass, mock_entry)
    
    msg = MagicMock()
    msg.payload = SAMPLE_PAYLOAD
    
    with patch("custom_components.rtl_433_discover.discovery_manager.dr.async_get") as mock_dr_get, \
         patch("custom_components.rtl_433_discover.discovery_manager.async_dispatcher_send") as mock_dispatch:
             
        await manager.async_process_message(msg)
        
        assert not mock_dr_get.called
