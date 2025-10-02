import asyncio

import pytest

from django.test import TestCase

from chargers.models import Charger, Transaction
from chargers.services import ChargerService, TransactionService


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_charger_service_async():
    """Test that ChargerService methods are properly async"""
    service = ChargerService()

    # Test async on_connected
    charger = await service.on_connected("EVSE-ASYNC-TEST", "TestVendor", "TestModel")
    assert charger.id == "EVSE-ASYNC-TEST"
    assert charger.vendor == "TestVendor"
    assert charger.model == "TestModel"

    # Test async on_heartbeat
    await service.on_heartbeat("EVSE-ASYNC-TEST")

    # Verify charger was updated
    updated_charger = await Charger.objects.aget(id="EVSE-ASYNC-TEST")
    assert updated_charger.last_heartbeat is not None


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_transaction_service_async():
    """Test that TransactionService methods are properly async"""
    # First create a charger
    charger_service = ChargerService()
    await charger_service.on_connected("EVSE-TX-TEST", "TestVendor", "TestModel")

    # Test async transaction start
    tx_service = TransactionService()
    tx = await tx_service.start("EVSE-TX-TEST", 1, "RFID123", 1000)

    assert tx.charger.id == "EVSE-TX-TEST"
    assert tx.connector_id == 1
    assert tx.id_tag == "RFID123"
    assert tx.meter_start == 1000

    # Test async transaction stop
    stopped_tx = await tx_service.stop(tx.transaction_id, "EVSE-TX-TEST", 2000)
    assert stopped_tx.meter_stop == 2000
    assert stopped_tx.status == "stopped"


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test that multiple async operations can run concurrently"""
    service = ChargerService()

    # Create multiple chargers concurrently
    tasks = []
    for i in range(5):
        task = service.on_connected(f"EVSE-CONCURRENT-{i}", f"Vendor{i}", f"Model{i}")
        tasks.append(task)

    # Wait for all to complete
    chargers = await asyncio.gather(*tasks)

    # Verify all chargers were created
    assert len(chargers) == 5
    for i, charger in enumerate(chargers):
        assert charger.id == f"EVSE-CONCURRENT-{i}"
        assert charger.vendor == f"Vendor{i}"
        assert charger.model == f"Model{i}"


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_performance():
    """Test that async operations don't block each other"""
    import time

    service = ChargerService()

    # Record start time
    start_time = time.time()

    # Create 10 chargers concurrently
    tasks = []
    for i in range(10):
        task = service.on_connected(f"EVSE-PERF-{i}", "TestVendor", "TestModel")
        tasks.append(task)

    # Wait for all to complete
    await asyncio.gather(*tasks)

    # Record end time
    end_time = time.time()
    duration = end_time - start_time

    # Should complete much faster than sequential operations
    # (This is a basic performance check)
    assert duration < 5.0  # Should complete in under 5 seconds

    # Verify all chargers were created
    charger_count = await Charger.objects.filter(id__startswith="EVSE-PERF-").acount()
    assert charger_count == 10
