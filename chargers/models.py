from django.db import models


class StatusChoices(models.TextChoices):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    AVAILABLE = "available"
    CHARGING = "charging"
    FAULTED = "faulted"

class Charger(models.Model):
    id = models.CharField(primary_key=True, max_length=64) # OCPP chargePointId
    vendor = models.CharField(max_length=128, blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=32, choices=StatusChoices.choices, default=StatusChoices.DISCONNECTED)
    last_heartbeat = models.DateTimeField(blank=True, null=True)
    connected_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.id


class TransactionStatusChoices(models.TextChoices):
    ACTIVE = "active"
    STOPPED = "stopped"

class Transaction(models.Model):
    transaction_id = models.BigAutoField(primary_key=True)
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name="transactions")
    connector_id = models.IntegerField()
    id_tag = models.CharField(max_length=128)
    meter_start = models.IntegerField(default=0)
    meter_stop = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=32, choices=TransactionStatusChoices.choices, default=TransactionStatusChoices.ACTIVE)


    def __str__(self):
        return f"{self.transaction_id} @ {self.charger_id}"




class EventLog(models.Model):
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name="logs")
    event = models.CharField(max_length=64)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"]



class ConnectorStatusChoices(models.TextChoices):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    FAULTED = "faulted"

class Connector(models.Model):
    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name="connectors")
    connector_id = models.IntegerField()
    status = models.CharField(max_length=32, choices=ConnectorStatusChoices.choices, default=ConnectorStatusChoices.AVAILABLE)
    last_heartbeat = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.charger_id} @ {self.connector_id}"



class ConnectorTransactionStatusChoices(models.TextChoices):
    ACTIVE = "active"
    STOPPED = "stopped"
    FAULTED = "faulted"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABORTED = "aborted"
    UNKNOWN = "unknown"

class ConnectorTransaction(models.Model):
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name="transactions")
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="connectors")
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.connector_id} @ {self.transaction_id}"


    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.connector_id} @ {self.transaction_id}"
    
