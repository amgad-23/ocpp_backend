"""DRF serializers for chargers, connectors, transactions, and logs."""

from rest_framework import serializers

from chargers.models import (
    Charger,
    Connector,
    ConnectorTransaction,
    EventLog,
    Transaction,
)


class ChargerSerializer(serializers.ModelSerializer):
    """Serialize `Charger` metadata and state."""
    class Meta:
        model = Charger
        fields = [
            "id",
            "vendor",
            "model",
            "status",
            "last_heartbeat",
            "connected_at",
            "updated_at",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    """Serialize `Transaction` including charger id via slug field."""
    charger = serializers.SlugRelatedField(slug_field="id", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "transaction_id",
            "charger",
            "connector_id",
            "id_tag",
            "meter_start",
            "meter_stop",
            "start_time",
            "stop_time",
            "status",
        ]


class EventLogSerializer(serializers.ModelSerializer):
    """Serialize `EventLog` entries with charger id."""
    charger = serializers.SlugRelatedField(slug_field="id", read_only=True)

    class Meta:
        model = EventLog
        fields = ["id", "charger", "event", "message", "created_at"]


class ConnectorSerializer(serializers.ModelSerializer):
    """Serialize `Connector` details and status."""
    charger = serializers.SlugRelatedField(slug_field="id", read_only=True)

    class Meta:
        model = Connector
        fields = [
            "id",
            "charger",
            "connector_id",
            "status",
            "last_heartbeat",
            "updated_at",
        ]


class ConnectorTransactionSerializer(serializers.ModelSerializer):
    """Serialize connector-to-transaction relationships."""
    connector = serializers.SlugRelatedField(slug_field="id", read_only=True)
    transaction = serializers.SlugRelatedField(slug_field="id", read_only=True)

    class Meta:
        model = ConnectorTransaction
        fields = ["id", "connector", "transaction", "updated_at"]


class ConnectorTransactionStatusSerializer(serializers.ModelSerializer):
    """Partial serializer to update a connector-transaction status."""
    class Meta:
        model = ConnectorTransaction
        fields = ["status"]


class TransactionStatusSerializer(serializers.ModelSerializer):
    """Partial serializer to update a transaction status."""
    class Meta:
        model = Transaction
        fields = ["status"]


class ConnectorStatusSerializer(serializers.ModelSerializer):
    """Partial serializer to update a connector status."""
    class Meta:
        model = Connector
        fields = ["status"]


class ChargerStatusSerializer(serializers.ModelSerializer):
    """Partial serializer to update a charger status."""
    class Meta:
        model = Charger
        fields = ["status"]


class ConnectorHeartbeatSerializer(serializers.ModelSerializer):
    """Partial serializer to update a connector heartbeat timestamp."""
    class Meta:
        model = Connector
        fields = ["last_heartbeat"]


class ChargerHeartbeatSerializer(serializers.ModelSerializer):
    """Partial serializer to update a charger heartbeat timestamp."""
    class Meta:
        model = Charger
        fields = ["last_heartbeat"]
