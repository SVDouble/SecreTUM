import pspython.pspyinstruments as pspyinstruments
import pspython.pspymethods as pspymethods
import logging
import time
import numpy as np
from scipy.stats import t

logging.basicConfig(level=logging.INFO)


def run(n_measurements=20):
    def new_data_callback(new_data):
        for type, value in new_data.items():
            print(type + ' = ' + str(value))
        return

    manager = pspyinstruments.InstrumentManager(new_data_callback=new_data_callback)
    instruments = manager.discover_instruments()
    # instruments = [pspyinstruments.Instrument(name='PalmSens4', conn=''), pspyinstruments.Instrument(name='EmStat Pico', conn='')]


    if not instruments:
        logging.error('No instruments found.')
        return
    else:
        # log the names of the found instruments with the respective index
        logging.info('Found instruments: \n' + ''.join([f'{i}: {instrument.name} \n' for i, instrument in enumerate(instruments)]))

    if len(instruments) == 1:
        instrument = instruments[0]
    else:
        # select the instrument by its index
        choice = int(input('Select the instrument by passing the index:'))
        instrument = instruments[choice]
    logging.info(f'Connecting to {instrument.name}')

    try:
        is_connected = manager.connect(instrument)
    except Exception as e:
        logging.error(f'Failed to connect to {instrument.name}: {e}')
        return
    
    if is_connected:
        logging.info(f'Successfully connected to {instrument.name}')


        # Scan Type: FixedPotential
        # Frequency Type: Scan
        # Equilibration Time: 0.0
        method = pspymethods.electrochemical_impedance_spectroscopy(**{'scan_type': 2, 'freq_type': 1, 'equilibration_time': 0.0, 'e_dc': 0.0, 'e_ac': 0.01, 'n_frequencies': n_measurements, 'max_frequency': 0.5, 'min_frequency': 0.5})
        
        try:
            measurement = manager.measure(method)
            if measurement is not None:
                logging.info('Measurement finished successfully.')
                return measurement

        except Exception as e:
            logging.error(f'Failed to start measurement: {e}')
            return
        
        # disconnect the manager
        try:
            manager.disconnect()
        except Exception as e:
            logging.error(f'Error while disconnecting: {e}')
            return
        logging.info('Disconnected successfully.')

    else:
        #TODO: Add reconnection logic
        return
    
    

        


def analyze_data(values):
    """
    Analyze a list of experimental values by calculating the mean, SEM, and a 95% confidence interval.
    Outliers are filtered using the 3-sigma rule.

    Parameters:
    values (list of float): List of experimental values.

    Returns:
    tuple: Returns the mean, SEM, and the 95% confidence interval of the filtered data.
    """
    # Ensure input is only floats or integers
    values = [value for value in values if isinstance(value, (float, int))]

    if not values:
        return None, None, (None, None)  # Return None if the list is empty or has no valid entries

    # Calculate initial mean and standard deviation
    mean = np.mean(values)
    std = np.std(values)

    # Filter outliers using the 3-sigma rule
    filtered_values = [x for x in values if (mean - 3*std) <= x <= (mean + 3*std)]

    if not filtered_values:
        return mean, None, (mean, mean)  # All values were outliers

    # Recalculate mean and SEM with filtered data
    mean_filtered = np.mean(filtered_values)
    std_filtered = np.std(filtered_values)
    sem_filtered = std_filtered / np.sqrt(len(filtered_values))

    # Calculate the 95% confidence interval for the mean
    confidence_interval = t.interval(0.95, len(filtered_values) - 1, loc=mean_filtered, scale=sem_filtered)

    return mean_filtered, sem_filtered, confidence_interval

    
    
    
    
        
if __name__ == '__main__':
    start = time.time()
    measurement = run(n_measurements=20)
    capacitance_list = measurement.cs_arrays[0]
    average_capacitance, sem, confidence_interval = analyze_data(capacitance_list)
    logging.info(f'Average capacitance: {average_capacitance} F')
    logging.info(f'Standard error of the mean: {sem} F')
    logging.info(f'95% Confidence interval: {confidence_interval} F')
    end = time.time()
    logging.info(f'Time elapsed: {end - start} seconds')
    




  