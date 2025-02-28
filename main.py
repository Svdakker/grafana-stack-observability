import logging
import time
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider


# Define a custom resource to monitor
resource = Resource(
    attributes={
        "service.name": "test-service",
        "service.version": "0.0.1",
        "job": "test-job"
    }
)

# Setup basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up OpenTelemetry logs
log_provider = LoggerProvider(resource=resource)
log_exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
logger.addHandler(LoggingHandler(logger_provider=log_provider))

# Set up OpenTelemetry metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True),
)
metrics_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider=metrics_provider)
meter = metrics.get_meter(__name__)
counter = meter.create_counter(
    name="test_counter",
    description="Counts in increments of 1",
    unit="1"
)

def main():
    count = 0
    try:
        while True:
            logger.info("Running...")
            count += 1
            counter.add(1)
            logger.info(f"Counter: {count}")
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        metrics_provider.shutdown()
        log_provider.shutdown()

if __name__ == "__main__":
    main()