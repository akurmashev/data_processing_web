# TEER Data Processing and Visualization Platform

## Overview
This platform is designed to process and visualize TEER (Transepithelial Electrical Resistance) data from experimental setups. It supports:
- Parsing `.mat` files containing measurement data and `.txt` files with timepoints.
- Storing raw and processed data in an SQLite database.
- Interactive visualization of impedance and phase differences using Dash.

## Features
- Automated ingestion of experimental data.
- Database schema for organizing raw and processed data.
- Interactive Dash dashboard for real-time exploration and filtering of results.

---

## Tools and Technologies
- **Python**: Core language for scripting and backend development.
- **Flask**: Backend framework for file uploads and API development.
- **Dash**: Framework for creating interactive visualizations.
- **SQLite**: Relational database for structured data storage.
- **MATLAB File Parsing**: `.mat` file handling via `scipy.io`.
- **Git and GitHub**: Version control and collaboration.

---

## Installation

### Prerequisites
- Python (3.8 or above)
- Git

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TEER_Data_Platform.git
   cd TEER_Data_Platform
