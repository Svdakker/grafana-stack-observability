import logging
import time
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up OpenTelemetry logs
log_provider = LoggerProvider(resource=resource)
log_exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
logger.addHandler(LoggingHandler(logger_provider=log_provider))

def main():
    try:
        while True:
            logger.info("Running...")
            logger.info("Sleeping for 5 seconds...")
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        log_provider.shutdown()

if __name__ == "__main__":
    main()