import dash
from dash import dcc, html, Input, Output
import pandas as pd
import sqlite3

# Database path
DB_PATH = '../data/measurement_data.db'

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to load processed data from the database
def load_processed_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT
        experiment_name,
        channel_name,
        cycle_index,
        timepoint,
        frequency,
        imp_2wire,
        imp_4wire,
        phase_2wire,
        phase_4wire,
        current_x,
        current_y,
        voltage_r
    FROM ProcessedData
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Load data initially
data = load_processed_data()

# Unique dropdown options
experiment_options = [{"label": exp, "value": exp} for exp in data['experiment_name'].unique()]
channel_options = [{"label": ch, "value": ch} for ch in data['channel_name'].unique()]
frequency_options = [{"label": f"{freq:.2f} Hz", "value": freq} for freq in sorted(data['frequency'].unique())]

# Layout
app.layout = html.Div([
    html.H1("TEER Data Visualization Platform", style={"textAlign": "center"}),

    # Filters
    html.Div([
        html.Div([
            html.Label("Experiment"),
            dcc.Dropdown(
                id="experiment-filter",
                options=experiment_options,
                placeholder="Select an experiment",
                multi=False
            ),
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div([
            html.Label("Channel"),
            dcc.Dropdown(
                id="channel-filter",
                options=channel_options,
                placeholder="Select a channel",
                multi=False
            ),
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div([
            html.Label("Frequency"),
            dcc.Dropdown(
                id="frequency-filter",
                options=frequency_options,
                placeholder="Select a frequency",
                multi=False
            ),
        ], style={"width": "30%", "display": "inline-block"}),
    ], style={"marginBottom": "20px"}),

    # Graphs
    html.Div([
        dcc.Graph(id="impedance-graph"),
        dcc.Graph(id="phase-graph"),
    ]),
])

# Callbacks for interactivity
@app.callback(
    [Output("impedance-graph", "figure"),
     Output("phase-graph", "figure")],
    [Input("experiment-filter", "value"),
     Input("channel-filter", "value"),
     Input("frequency-filter", "value")]
)
def update_graphs(experiment_name, channel_name, frequency):
    filtered_data = data

    # Apply filters
    if experiment_name:
        filtered_data = filtered_data[filtered_data['experiment_name'] == experiment_name]
    if channel_name:
        filtered_data = filtered_data[filtered_data['channel_name'] == channel_name]
    if frequency:
        filtered_data = filtered_data[filtered_data['frequency'] == frequency]

    # Impedance graph
    impedance_fig = {
        "data": [
            {"x": filtered_data["cycle_index"], "y": filtered_data["imp_2wire"], "type": "line", "name": "2-Wire Impedance"},
            {"x": filtered_data["cycle_index"], "y": filtered_data["imp_4wire"], "type": "line", "name": "4-Wire Impedance"},
        ],
        "layout": {"title": "Impedance Over Cycles", "xaxis": {"title": "Cycle Index"}, "yaxis": {"title": "Impedance (Ohms)"}},
    }

    # Phase graph
    phase_fig = {
        "data": [
            {"x": filtered_data["frequency"], "y": filtered_data["phase_2wire"], "type": "line", "name": "2-Wire Phase"},
            {"x": filtered_data["frequency"], "y": filtered_data["phase_4wire"], "type": "line", "name": "4-Wire Phase"},
        ],
        "layout": {"title": "Phase Differences Across Frequencies", "xaxis": {"title": "Frequency (Hz)"}, "yaxis": {"title": "Phase (Degrees)"}},
    }

    return impedance_fig, phase_fig

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
