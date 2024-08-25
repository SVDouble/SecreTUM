import logging

import numpy as np
import redis
from scipy.stats import t  # Assuming you need scipy for statistical calculations

from pspython import pspyinstruments, pspymethods

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Set up Redis connection
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
redis_pubsub = redis_client.pubsub()
redis_pubsub.subscribe("sensor:trigger")

# Redis TimeSeries configuration
RETENTION_PERIOD_MS = 30 * 24 * 60 * 60 * 1000  # 1 month in milliseconds


def echo_new_data(new_data):
    """Callback function to print new data."""
    for type_, value in new_data.items():
        print(f"{type_} = {value}")


def select_instrument(instruments):
    """Prompt user to select an instrument."""
    if len(instruments) == 1:
        return instruments[0]

    print("Available instruments:")
    for i, instrument in enumerate(instruments):
        print(f"{i}: {instrument.name}")

    choice = int(input("Select the instrument by passing the index: "))
    return instruments[choice]


def store_to_redis(timeseries_key, value):
    """Store a measurement value to Redis TimeSeries with a retention policy."""
    redis_client.ts().create(timeseries_key, retention_msecs=RETENTION_PERIOD_MS)
    redis_client.ts().add(timeseries_key, "*", value)


def run_measurements(n_measurements=20):
    """Main function to run the measurement."""
    manager = pspyinstruments.InstrumentManager(new_data_callback=echo_new_data)
    instruments = pspyinstruments.discover_instruments()

    if not instruments:
        logging.error("No instruments found.")
        return None

    logging.info(
        "Found instruments: "
        + ", ".join(f"{i}: {instr.name}" for i, instr in enumerate(instruments))
    )

    instrument = select_instrument(instruments)
    logging.info(f"Connecting to {instrument.name}")

    try:
        is_connected = manager.connect(instrument)
        if not is_connected:
            logging.error(f"Failed to connect to {instrument.name}")
            return None
        logging.info(f"Successfully connected to {instrument.name}")
    except Exception as e:
        logging.error(f"Failed to connect to {instrument.name}: {e}")
        return None

    # Measurement configuration
    method = pspymethods.electrochemical_impedance_spectroscopy(
        scan_type=2,
        freq_type=1,
        equilibration_time=0.0,
        e_dc=0.0,
        e_ac=0.01,
        n_frequencies=n_measurements,
        max_frequency=0.5,
        min_frequency=0.5,
    )

    try:
        measurement = manager.measure(method)
        if measurement is not None:
            logging.info("Measurement finished successfully.")
            return measurement
    except Exception as e:
        logging.error(f"Failed to start measurement: {e}")
        return None
    finally:
        # Ensure disconnection in all cases
        try:
            manager.disconnect()
            logging.info("Disconnected successfully.")
        except Exception as e:
            logging.error(f"Error while disconnecting: {e}")

    return None


def analyze_data(values):
    """Analyze a list of experimental values by calculating the mean, SEM, and a 95% confidence interval."""
    values = [v for v in values if isinstance(v, (float, int))]
    if not values:
        return None, None, (None, None)

    mean = np.mean(values)
    std = np.std(values)
    filtered_values = [x for x in values if (mean - 3 * std) <= x <= (mean + 3 * std)]

    if not filtered_values:
        return mean, None, (mean, mean)

    mean_filtered = np.mean(filtered_values)
    sem_filtered = np.std(filtered_values) / np.sqrt(len(filtered_values))
    confidence_interval = t.interval(
        0.95, len(filtered_values) - 1, loc=mean_filtered, scale=sem_filtered
    )

    return mean_filtered, sem_filtered, confidence_interval


def listen_for_triggers():
    """Listen to Redis Pub/Sub channel for measurement triggers."""
    logging.info(
        "Listening for measurement triggers on Redis channel 'measurement_trigger'."
    )
    for message in redis_pubsub.listen():
        if message["type"] == "message":
            logging.info(f"Received trigger: {message['data']}")
            m = run_measurements(n_measurements=20)
            if m:
                capacitance_list = m.cs_arrays[0]
                avg_capacitance, sem, confidence_interval = analyze_data(
                    capacitance_list
                )
                logging.info(f"Average capacitance: {avg_capacitance} F")
                logging.info(f"Standard error of the mean: {sem} F")
                logging.info(f"95% Confidence interval: {confidence_interval} F")

                # Store the average capacitance to Redis TimeSeries
                store_to_redis("sensor:capacitance", avg_capacitance)


if __name__ == "__main__":
    listen_for_triggers()
