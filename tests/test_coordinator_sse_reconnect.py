"""Regression tests for SSE reconnect state refetch.

The Electrolux SDK's ``start_event_stream`` runs an indefinite loop that
auto-reconnects internally on connection drops (sleeping 10s between attempts)
and invokes its ``do_on_livestream_opening_list`` callbacks on *every*
successful (re)connect. The SSE stream only delivers change events going
forward — it does NOT replay events missed during the disconnect window.

If the coordinator does not refetch appliance state on each reconnect, any
state transition that happened during the gap (e.g. a washer cycle finishing
and the appliance returning to IDLE) is lost: automations watching for the
"finished" state never fire, and the entity briefly shows "unknown" before
jumping straight to idle.

These tests pin the contract: the coordinator must wire an ``on_connected``
callback that performs a full state refetch, so reconnects re-sync state.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.electrolux.coordinator import ElectroluxCoordinator


def _make_create_task_mock(rv=None):
    def _side_effect(coro):
        if asyncio.iscoroutine(coro):
            coro.close()
        return rv

    return MagicMock(side_effect=_side_effect)


@pytest.fixture
def mock_hass():
    mock_loop = MagicMock()
    mock_loop.time.return_value = 1_000_000.0
    hass = MagicMock()
    hass.loop = mock_loop
    hass.async_create_task = _make_create_task_mock()
    return hass


@pytest.fixture
def coordinator(mock_hass):
    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__",
        return_value=None,
    ):
        coord = ElectroluxCoordinator.__new__(ElectroluxCoordinator)
        coord.hass = mock_hass
        coord.api = MagicMock()
        coord._last_update_times = {}
        coord._last_known_connectivity = {}
        coord.async_set_updated_data = MagicMock()
        return coord


def _make_appliances(app_ids):
    appliances = MagicMock()
    app_map = {aid: MagicMock() for aid in app_ids}
    appliances.appliances = app_map
    appliances.get_appliances.return_value = app_map
    appliances.get_appliance_ids.return_value = list(app_ids)
    return appliances


@pytest.mark.asyncio
async def test_reconnect_triggers_state_refetch(coordinator):
    """The on_connected hook fired by the SDK on every reconnect must refetch state."""
    appliances = _make_appliances(["wm1"])
    coordinator.data = {"appliances": appliances}
    coordinator._appliances_cache = appliances

    captured = {}

    async def fake_watch(ids, callback, on_connected=None):
        # The SDK invokes on_connected on every (re)connect; capture it so we
        # can simulate a reconnect below.
        captured["on_connected"] = on_connected

    coordinator.api.watch_for_appliance_state_updates = AsyncMock(
        side_effect=fake_watch
    )
    coordinator.api.get_appliance_state = AsyncMock(
        return_value={"connectivityState": "connected"}
    )

    await coordinator.listen_websocket()

    # Contract: the coordinator must hand the SDK an on_connected callback,
    # otherwise the SDK's internal reconnects silently skip the refetch.
    assert (
        captured.get("on_connected") is not None
    ), "on_connected not wired — SDK reconnects will not refetch missed state"

    # Simulate the SDK reconnecting after a dropped stream.
    coordinator.api.get_appliance_state.reset_mock()
    await captured["on_connected"]()

    assert coordinator.api.get_appliance_state.await_count == 1, (
        "reconnect did not refetch appliance state — cycle-end transitions "
        "during the disconnect window are lost"
    )
