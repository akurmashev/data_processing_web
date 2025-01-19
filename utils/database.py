import sqlite3
import pandas as pd
import numpy as np

def initialize_database(db_path):
    """Creates the database schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Channels table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Channels (
        channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
        experiment_name TEXT,
        channel_name TEXT,
        file_name TEXT UNIQUE,
        total_cycles INTEGER
    );
    """)

    # Create Cycles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cycles (
        cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id INTEGER,
        channel_name TEXT,
        cycle_index INTEGER,
        timepoint REAL,
        FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
    );
    """)

    # Create Frequencies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Frequencies (
        frequency_id INTEGER PRIMARY KEY AUTOINCREMENT,
        frequency REAL UNIQUE
    );
    """)

    # Create CurrentMeasurements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CurrentMeasurements (
        measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id INTEGER,
        channel_name TEXT,
        experiment_name TEXT,
        cycle_index INTEGER,
        frequency_id INTEGER,
        x REAL,
        y REAL,
        phase REAL,
        r REAL,
        auxin0 REAL,
        auxin0pwr REAL,
        auxin0stddev REAL,
        auxin1 REAL,
        auxin1pwr REAL,
        auxin1stddev REAL,
        bandwidth REAL,
        frequencypwr REAL,
        frequencystddev REAL,
        grid REAL,
        rpwr REAL,
        rstddev REAL,
        settling REAL,
        tc REAL,
        tcmeas REAL,
        xpwr REAL,
        xstddev REAL,
        ypwr REAL,
        ystddev REAL,
        count INTEGER,
        nexttimestamp REAL,
        settimestamp REAL,
        FOREIGN KEY (cycle_index) REFERENCES Cycles(cycle_index),
        FOREIGN KEY (frequency_id) REFERENCES Frequencies(frequency_id)
    );
    """)

    # Create VoltageMeasurements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS VoltageMeasurements (
        measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id INTEGER,
        channel_name TEXT,
        experiment_name TEXT,
        cycle_index INTEGER,
        frequency_id INTEGER,
        x REAL,
        y REAL,
        phase REAL,
        r REAL,
        auxin0 REAL,
        auxin0pwr REAL,
        auxin0stddev REAL,
        auxin1 REAL,
        auxin1pwr REAL,
        auxin1stddev REAL,
        bandwidth REAL,
        frequencypwr REAL,
        frequencystddev REAL,
        grid REAL,
        rpwr REAL,
        rstddev REAL,
        settling REAL,
        tc REAL,
        tcmeas REAL,
        xpwr REAL,
        xstddev REAL,
        ypwr REAL,
        ystddev REAL,
        count INTEGER,
        nexttimestamp REAL,
        settimestamp REAL,
        FOREIGN KEY (cycle_index) REFERENCES Cycles(cycle_index),
        FOREIGN KEY (frequency_id) REFERENCES Frequencies(frequency_id)
    );
    """)

    # Create ProcessedData table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ProcessedData (
        processed_id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_name TEXT,
        experiment_name TEXT,
        cycle_index INTEGER,
        timepoint REAL,
        frequency REAL,
        imp_2wire REAL,
        imp_4wire REAL,
        phase_2wire REAL,
        phase_4wire REAL,
        current_x REAL,
        current_y REAL,
        voltage_r REAL,
        phase_voltage_4wire REAL,
        phase_current REAL           
    );
    """)

    conn.commit()
    conn.close()


def insert_data(db_path, mat_data, timepoints, experiment_name, channel_name):
    """
    Insert parsed .mat and timepoint data into the database.
    """
    import sqlite3
    import pandas as pd

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Extract relevant data
    total_cycles = len(timepoints)
    frequencies = mat_data['frequencies']
    cycles = mat_data['cycles']

    # Insert into Channels table
    cursor.execute("""
    INSERT OR IGNORE INTO Channels (experiment_name, channel_name, file_name, total_cycles)
    VALUES (?, ?, ?, ?)
    """, (experiment_name, channel_name, f"{experiment_name}-{channel_name}", total_cycles))
    channel_id = cursor.lastrowid or cursor.execute(
        "SELECT channel_id FROM Channels WHERE experiment_name = ? AND channel_name = ?;",
        (experiment_name, channel_name)
    ).fetchone()[0]

    # Insert frequencies
    for freq in frequencies:
        cursor.execute("INSERT OR IGNORE INTO Frequencies (frequency) VALUES (?)", (freq,))

    # Insert cycles and measurements
    for cycle_index, cycle_data in enumerate(cycles, start=1):  # cycle_index starts at 1
        timepoint = timepoints[cycle_index - 1]

        # Insert into Cycles table
        cursor.execute("""
        INSERT INTO Cycles (channel_id, channel_name, cycle_index, timepoint)
        VALUES (?, ?, ?, ?)
        """, (channel_id, channel_name, cycle_index, timepoint))

        # Insert CurrentMeasurements
        current_sample = pd.DataFrame(cycle_data['current_measurements'])
        for i, freq in enumerate(frequencies):
            cursor.execute("""
            INSERT INTO CurrentMeasurements (
                channel_id, channel_name, experiment_name, cycle_index, frequency_id, x, y, phase, r,
                auxin0, auxin0pwr, auxin0stddev, auxin1, auxin1pwr, auxin1stddev,
                bandwidth, frequencypwr, frequencystddev, grid, rpwr, rstddev, settling, tc, tcmeas,
                xpwr, xstddev, ypwr, ystddev, count, nexttimestamp, settimestamp
            ) VALUES (
                ?, ?, ?, ?, (SELECT frequency_id FROM Frequencies WHERE frequency = ?), ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """, (
                channel_id, channel_name, experiment_name, cycle_index, freq,
                current_sample['x'][i], current_sample['y'][i], current_sample['phase'][i], current_sample['r'][i],
                current_sample['auxin0'][i], current_sample['auxin0pwr'][i], current_sample['auxin0stddev'][i],
                current_sample['auxin1'][i], current_sample['auxin1pwr'][i], current_sample['auxin1stddev'][i],
                current_sample['bandwidth'][i], current_sample['frequencypwr'][i], current_sample['frequencystddev'][i],
                current_sample['grid'][i], current_sample['rpwr'][i], current_sample['rstddev'][i],
                current_sample['settling'][i], current_sample['tc'][i], current_sample['tcmeas'][i],
                current_sample['xpwr'][i], current_sample['xstddev'][i], current_sample['ypwr'][i],
                current_sample['ystddev'][i], current_sample['count'][i],
                current_sample['nexttimestamp'][i], current_sample['settimestamp'][i]
            ))

        # Insert VoltageMeasurements
        voltage_sample = pd.DataFrame(cycle_data['voltage_measurements'])
        for i, freq in enumerate(frequencies):
            cursor.execute("""
            INSERT INTO VoltageMeasurements (
                channel_id, channel_name, experiment_name, cycle_index, frequency_id, x, y, phase, r,
                auxin0, auxin0pwr, auxin0stddev, auxin1, auxin1pwr, auxin1stddev,
                bandwidth, frequencypwr, frequencystddev, grid, rpwr, rstddev, settling, tc, tcmeas,
                xpwr, xstddev, ypwr, ystddev, count, nexttimestamp, settimestamp
            ) VALUES (
                ?, ?, ?, ?, (SELECT frequency_id FROM Frequencies WHERE frequency = ?), ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """, (
                channel_id, channel_name, experiment_name, cycle_index, freq,
                voltage_sample['x'][i], voltage_sample['y'][i], voltage_sample['phase'][i], voltage_sample['r'][i],
                voltage_sample['auxin0'][i], voltage_sample['auxin0pwr'][i], voltage_sample['auxin0stddev'][i],
                voltage_sample['auxin1'][i], voltage_sample['auxin1pwr'][i], voltage_sample['auxin1stddev'][i],
                voltage_sample['bandwidth'][i], voltage_sample['frequencypwr'][i], voltage_sample['frequencystddev'][i],
                voltage_sample['grid'][i], voltage_sample['rpwr'][i], voltage_sample['rstddev'][i],
                voltage_sample['settling'][i], voltage_sample['tc'][i], voltage_sample['tcmeas'][i],
                voltage_sample['xpwr'][i], voltage_sample['xstddev'][i], voltage_sample['ypwr'][i],
                voltage_sample['ystddev'][i], voltage_sample['count'][i],
                voltage_sample['nexttimestamp'][i], voltage_sample['settimestamp'][i]
            ))

    conn.commit()
    conn.close()




def populate_processed_data(db_path, amplitude=0.2, rtia=1000):
    """
    Processes raw data and populates the ProcessedData table.
    """
    import numpy as np
    import pandas as pd

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Constants
    rad_to_deg = 180 / np.pi

    # Fetch all channels
    channels_query = "SELECT channel_id, channel_name, experiment_name FROM Channels;"
    channels = pd.read_sql_query(channels_query, conn)

    for _, channel in channels.iterrows():
        channel_id = channel['channel_id']
        channel_name = channel['channel_name']
        experiment_name = channel['experiment_name']

        # Fetch cycles for the current channel
        cycles_query = f"SELECT * FROM Cycles WHERE channel_id = {channel_id};"
        cycles = pd.read_sql_query(cycles_query, conn)

        # Fetch frequencies
        frequencies_query = "SELECT * FROM Frequencies;"
        frequencies = pd.read_sql_query(frequencies_query, conn)['frequency'].values

        # Fetch current and voltage measurements for the channel
        current_query = f"""
        SELECT * FROM CurrentMeasurements WHERE channel_id = {channel_id};
        """
        current_df = pd.read_sql_query(current_query, conn)

        voltage_query = f"""
        SELECT * FROM VoltageMeasurements WHERE channel_id = {channel_id};
        """
        voltage_df = pd.read_sql_query(voltage_query, conn)

        # Process each cycle
        for _, cycle in cycles.iterrows():
            cycle_index = cycle['cycle_index']
            timepoint = cycle['timepoint']

            # Filter measurements for the current cycle
            current_cycle = current_df[current_df['cycle_index'] == cycle_index]
            voltage_cycle = voltage_df[voltage_df['cycle_index'] == cycle_index]

            for freq_idx, freq in enumerate(frequencies):
                # Extract current and voltage data
                ix = current_cycle.iloc[freq_idx]['x']
                print(ix)
                iy = current_cycle.iloc[freq_idx]['y']
                print(iy)
                voltage_r = voltage_cycle.iloc[freq_idx]['r']
                print(voltage_r)
                phase_voltage_4wire = voltage_cycle.iloc[freq_idx]['phase']
                print(phase_voltage_4wire)
                phase_current = current_cycle.iloc[freq_idx]['phase'] + np.pi
                print(phase_current)


                # Calculate phase differences
                phase_2wire_val = 0
                phase_4wire_val = np.unwrap([phase_voltage_4wire - phase_current]) * rad_to_deg
                print(phase_4wire_val)

                # Calculate impedances
                imp_2wire_val = abs(amplitude / np.sqrt(2) * rtia / (ix + 1j * iy))
                imp_4wire_val = abs(voltage_r * rtia / (ix + 1j * iy))

                # Insert processed data into the database
                cursor.execute("""
                INSERT INTO ProcessedData (
                    channel_name, experiment_name, cycle_index, timepoint, frequency,
                    imp_2wire, imp_4wire, phase_2wire, phase_4wire,
                    current_x, current_y, voltage_r, phase_voltage_4wire, phase_current
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    channel_name, experiment_name, cycle_index, timepoint, freq,
                    imp_2wire_val, imp_4wire_val, phase_2wire_val, phase_4wire_val[0],
                    ix, iy, voltage_r, phase_voltage_4wire, phase_current
                ))

    conn.commit()
    conn.close()




