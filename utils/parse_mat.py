import scipy.io

def parse_mat_file(filepath):
    """
    Parses a .mat file and returns its structured content for database ingestion.
    """
    # Load the .mat file
    mat_data = scipy.io.loadmat(filepath, struct_as_record=True, squeeze_me=True, simplify_cells=True)

    # Ensure 'results' key exists
    if 'results' not in mat_data:
        raise KeyError(f"'results' key not found in the .mat file: {filepath}")

    # Extract primary fields from the 'results' structure
    results = mat_data['results']
    frequencies = results['frequencies']  # Array of frequencies
    total_cycles = int(results['cc'])  # Total number of cycles
    all_data = results['all']  # Per-cycle data

    # Parse each cycle's data
    cycles_data = []
    for cycle_index, cycle in enumerate(all_data):
        demods = all_data[cycle_index]['dev1495']['demods']

        # Extract current and voltage samples
        current_sample = demods[0]['sample']
        voltage_sample = demods[1]['sample']

        # Parse individual measurement data
        current_measurements = []
        voltage_measurements = []

        for i, frequency in enumerate(frequencies):
            current_measurements.append({
                'frequency': frequency,
                'auxin0': current_sample['auxin0'][i],
                'auxin0pwr': current_sample['auxin0pwr'][i],
                'auxin0stddev': current_sample['auxin0stddev'][i],
                'auxin1': current_sample['auxin1'][i],
                'auxin1pwr': current_sample['auxin1pwr'][i],
                'auxin1stddev': current_sample['auxin1stddev'][i],
                'bandwidth': current_sample['bandwidth'][i],
                'frequencypwr': current_sample['frequencypwr'][i],
                'frequencystddev': current_sample['frequencystddev'][i],
                'grid': current_sample['grid'][i],
                'phase': current_sample['phase'][i],
                'phasepwr': current_sample['phasepwr'][i],
                'phasestddev': current_sample['phasestddev'][i],
                'r': current_sample['r'][i],
                'rpwr': current_sample['rpwr'][i],
                'rstddev': current_sample['rstddev'][i],
                'settling': current_sample['settling'][i],
                'tc': current_sample['tc'][i],
                'tcmeas': current_sample['tcmeas'][i],
                'x': current_sample['x'][i],
                'xpwr': current_sample['xpwr'][i],
                'xstddev': current_sample['xstddev'][i],
                'y': current_sample['y'][i],
                'ypwr': current_sample['ypwr'][i],
                'ystddev': current_sample['ystddev'][i],
                'count': current_sample['count'][i],
                'nexttimestamp': current_sample['nexttimestamp'][i],
                'settimestamp': current_sample['settimestamp'][i],
            })

            voltage_measurements.append({
                'frequency': frequency,
                'auxin0': voltage_sample['auxin0'][i],
                'auxin0pwr': voltage_sample['auxin0pwr'][i],
                'auxin0stddev': voltage_sample['auxin0stddev'][i],
                'auxin1': voltage_sample['auxin1'][i],
                'auxin1pwr': voltage_sample['auxin1pwr'][i],
                'auxin1stddev': voltage_sample['auxin1stddev'][i],
                'bandwidth': voltage_sample['bandwidth'][i],
                'frequencypwr': voltage_sample['frequencypwr'][i],
                'frequencystddev': voltage_sample['frequencystddev'][i],
                'grid': voltage_sample['grid'][i],
                'phase': voltage_sample['phase'][i],
                'phasepwr': voltage_sample['phasepwr'][i],
                'phasestddev': voltage_sample['phasestddev'][i],
                'r': voltage_sample['r'][i],
                'rpwr': voltage_sample['rpwr'][i],
                'rstddev': voltage_sample['rstddev'][i],
                'settling': voltage_sample['settling'][i],
                'tc': voltage_sample['tc'][i],
                'tcmeas': voltage_sample['tcmeas'][i],
                'x': voltage_sample['x'][i],
                'xpwr': voltage_sample['xpwr'][i],
                'xstddev': voltage_sample['xstddev'][i],
                'y': voltage_sample['y'][i],
                'ypwr': voltage_sample['ypwr'][i],
                'ystddev': voltage_sample['ystddev'][i],
                'count': voltage_sample['count'][i],
                'nexttimestamp': voltage_sample['nexttimestamp'][i],
                'settimestamp': voltage_sample['settimestamp'][i],
            })

        # Append cycle data
        cycles_data.append({
            'cycle_index': cycle_index + 1,
            'timepoint': cycle['timePoint'],
            'current_measurements': current_measurements,
            'voltage_measurements': voltage_measurements
        })

    # Return structured data for database ingestion
    parsed_data = {
        'frequencies': frequencies,
        'total_cycles': total_cycles,
        'cycles': cycles_data
    }

    return parsed_data
