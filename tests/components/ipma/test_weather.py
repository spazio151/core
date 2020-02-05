"""The tests for the IPMA weather component."""
from collections import namedtuple
from unittest.mock import patch

from homeassistant.components import weather
from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_SPEED,
    DOMAIN as WEATHER_DOMAIN,
)
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry, mock_coro

TEST_CONFIG = {"name": "HomeTown", "latitude": "40.00", "longitude": "-8.00"}


class MockLocation:
    """Mock Location from pyipma."""

    async def observation(self, api):
        """Mock Observation."""
        Observation = namedtuple(
            "Observation",
            [
                "accumulated_precipitation",
                "humidity",
                "pressure",
                "radiation",
                "temperature",
                "wind_direction",
                "wind_intensity_km",
            ],
        )

        return Observation(0.0, 71.0, 1000.0, 0.0, 18.0, "NW", 3.94)

    async def forecast(self, api):
        """Mock Forecast."""
        Forecast = namedtuple(
            "Forecast",
            [
                "feels_like_temperature",
                "forecast_date",
                "forecasted_hours",
                "humidity",
                "max_temperature",
                "min_temperature",
                "precipitation_probability",
                "temperature",
                "update_date",
                "weather_type",
                "wind_direction",
                "wind_strength",
            ],
        )

        return [
            Forecast(
                None,
                "2020-01-15T00:00:00",
                24,
                None,
                16.2,
                10.6,
                "100.0",
                13.4,
                "2020-01-15T07:51:00",
                9,
                "S",
                None,
            ),
            Forecast(
                "7.7",
                "2020-01-15T02:00:00",
                1,
                "86.9",
                None,
                None,
                "-99.0",
                10.6,
                "2020-01-15T07:51:00",
                10,
                "S",
                "32.7",
            ),
        ]

    @property
    def name(self):
        """Mock location."""
        return "HomeTown"

    @property
    def station_latitude(self):
        """Mock latitude."""
        return 0

    @property
    def global_id_local(self):
        """Mock global identifier of the location."""
        return 1130600

    @property
    def id_station(self):
        """Mock identifier of the station."""
        return 1200545

    @property
    def station_longitude(self):
        """Mock longitude."""
        return 0


async def test_setup_configuration(hass):
    """Test for successfully setting up the IPMA platform."""
    with patch(
        "homeassistant.components.ipma.weather.async_get_location",
        return_value=mock_coro(MockLocation()),
    ):
        assert await async_setup_component(
            hass, weather.DOMAIN, {"weather": {"name": "HomeTown", "platform": "ipma"}}
        )
    await hass.async_block_till_done()

    state = hass.states.get("weather.hometown")
    assert state.state == "rainy"

    data = state.attributes
    assert data.get(ATTR_WEATHER_TEMPERATURE) == 18.0
    assert data.get(ATTR_WEATHER_HUMIDITY) == 71
    assert data.get(ATTR_WEATHER_PRESSURE) == 1000.0
    assert data.get(ATTR_WEATHER_WIND_SPEED) == 3.94
    assert data.get(ATTR_WEATHER_WIND_BEARING) == "NW"
    assert state.attributes.get("friendly_name") == "HomeTown"


async def test_setup_config_flow(hass):
    """Test for successfully setting up the IPMA platform."""
    with patch(
        "homeassistant.components.ipma.weather.async_get_location",
        return_value=mock_coro(MockLocation()),
    ):
        entry = MockConfigEntry(domain="ipma", data=TEST_CONFIG)
        await hass.config_entries.async_forward_entry_setup(entry, WEATHER_DOMAIN)
        await hass.async_block_till_done()

    state = hass.states.get("weather.hometown")
    assert state.state == "rainy"

    data = state.attributes
    assert data.get(ATTR_WEATHER_TEMPERATURE) == 18.0
    assert data.get(ATTR_WEATHER_HUMIDITY) == 71
    assert data.get(ATTR_WEATHER_PRESSURE) == 1000.0
    assert data.get(ATTR_WEATHER_WIND_SPEED) == 3.94
    assert data.get(ATTR_WEATHER_WIND_BEARING) == "NW"
    assert state.attributes.get("friendly_name") == "HomeTown"
