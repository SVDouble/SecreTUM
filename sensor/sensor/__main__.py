import logging

import numpy as np
import redis
from scipy.stats import t

from pspython import pspyinstruments, pspymethods

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Redis TimeSeries configuration
RETENTION_PERIOD_MS = 30 * 24 * 60 * 60 * 1000  # 1 month in milliseconds
TRIGGER_CHANNEL = "sensor:trigger"
UPDATE_CHANNEL = "sensor:update"
TIMESERIES_KEY = "sensor:measurements"
MEASUREMENT_KEY = "sensor:measurement"

REDIS_HOST = "secretum"  # IP address of the host machine
N_MEASUREMENTS = 20

# Set up Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
redis_pubsub = redis_client.pubsub()
redis_pubsub.subscribe(TRIGGER_CHANNEL)


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


def store_to_redis(value):
    """Store a measurement value to Redis TimeSeries with a retention policy."""
    #redis_client.ts().create(TIMESERIES_KEY, retention_msecs=RETENTION_PERIOD_MS)
    #redis_client.ts().add(TIMESERIES_KEY, "*", value)
    redis_client.set(MEASUREMENT_KEY, value)


def notify_controller():
    """Notify the controller that the measurement is complete."""
    redis_client.publish(UPDATE_CHANNEL, "complete")


def remove_previous_measurement():
    redis_client.delete(MEASUREMENT_KEY)


def run_measurements(n_measurements):
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
        f"Listening for measurement triggers on Redis channel '{TRIGGER_CHANNEL}'."
    )
    for message in redis_pubsub.listen():
        if message["type"] == "message":
            logging.info(f"Received trigger: {message['data']}")
            remove_previous_measurement()
            m = run_measurements(n_measurements=N_MEASUREMENTS)
            if m:
                capacitance_list = m.cs_arrays[0]
                avg_capacitance, sem, confidence_interval = analyze_data(
                    capacitance_list
                )
                logging.info(f"Average capacitance: {avg_capacitance} F")
                logging.info(f"Standard error of the mean: {sem} F")
                logging.info(f"95% Confidence interval: {confidence_interval} F")

                # Store the average capacitance to Redis TimeSeries
                store_to_redis(avg_capacitance)
            else:
                logging.error("Measurement failed.")
            notify_controller()


if __name__ == "__main__":
    listen_for_triggers()
