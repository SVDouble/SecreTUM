import pspython.pspyinstruments as pspyinstruments
import pspython.pspymethods as pspymethods
import logging

logging.basicConfig(level=logging.INFO)


def run():
    def new_data_callback(new_data):
        for type, value in new_data.items():
            print(type + ' = ' + str(value))
        return

    manager = pspyinstruments.InstrumentManager(new_data_callback=new_data_callback)
    # instruments = manager.discover_instruments()
    instruments = [pspyinstruments.Instrument(name='PalmSens4', conn=''), pspyinstruments.Instrument(name='EmStat Pico', conn='')]


    if not instruments:
        logging.error('No instruments found.')
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


        # Scan Type: Potential
        # Frequency Type: Scan
        # Equilibration Time: 0.0
        method = pspymethods.electrochemical_impedance_spectroscopy(kwargs={'scan_type': 0, 'freq_type': 1, 'equilibration_time': 0.0, 'e_dc': 0.0, 'e_ac': 0.01, 'n_frequencies': 63, 'max_frequency': 0.6, 'min_frequency': 0.4})
        
        try:
            measurement = manager.measure(method)
            if measurement is not None:
                logging.info('Measurement finished successfully.')

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
    
    

        

        
if __name__ == '__main__':
    run()

    



  