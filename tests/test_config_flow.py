"""Test the rtl_433 Discovery config flow."""
from unittest.mock import patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.rtl_433_discover.const import DOMAIN, CONF_TOPIC_PREFIX, DEFAULT_TOPIC_PREFIX, CONF_IGNORE_DEVICES

async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] is None

    with patch(
        "custom_components.rtl_433_discover.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_TOPIC_PREFIX: "test/topic",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "rtl_433 Discovery"
    assert result2["data"] == {CONF_TOPIC_PREFIX: "test/topic"}
    assert len(mock_setup_entry.mock_calls) == 1

async def test_options_flow(hass: HomeAssistant) -> None:
    """Test options flow."""
    # Create an entry
    entry = config_entries.MockConfigEntry(
        domain=DOMAIN,
        data={CONF_TOPIC_PREFIX: "test/topic"},
    )
    entry.add_to_hass(hass)
    
    # Initialize options flow
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_IGNORE_DEVICES: "123, 456"},
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {CONF_IGNORE_DEVICES: "123, 456"}
