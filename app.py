from flask import Flask, request, jsonify
import os
import zipfile
from utils.parse_mat import parse_mat_file
from utils.parse_txt import parse_txt_file
from utils.database import initialize_database, insert_data, populate_processed_data

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = './uploads'
EXTRACT_FOLDER = os.path.join(UPLOAD_FOLDER, 'extracted')
os.makedirs(EXTRACT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database
DB_PATH = './data/measurement_data.db'
os.makedirs('./data', exist_ok=True)  # Ensure data directory exists
initialize_database(DB_PATH)


@app.route('/')
def home():
    return '''
    <h1>Welcome to the Data Processing Platform</h1>
    <p>Upload a zipped folder containing MATLAB result files and timepoints files using the <code>/upload</code> endpoint.</p>
    <p>The system will process the data and automatically generate a .csv file for download or visualization.</p>
    '''

@app.route('/upload', methods=['POST'])
def upload_folder():
    """Handles folder upload and processing."""
    try:
        # Ensure a zip file is provided
        if 'folder' not in request.files:
            return jsonify({"error": "Please upload a zipped folder of experimental files"}), 400

        zip_file = request.files['folder']

        # Validate file extension
        if not zip_file.filename.endswith('.zip'):
            return jsonify({"error": "Invalid file type. Please upload a .zip file"}), 400

        # Extract experiment name from the zip file name (before ".zip")
        experiment_name = os.path.splitext(zip_file.filename)[0]

        # Save and extract the zip file
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_file.filename)
        zip_file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_FOLDER)

        # Debugging: Log extracted files
        print(f"Files extracted to: {EXTRACT_FOLDER}")
        extracted_files = os.listdir(EXTRACT_FOLDER)
        print(f"Extracted files: {extracted_files}")

        # Search for .mat and .txt files
        import glob
        mat_files = glob.glob(os.path.join(EXTRACT_FOLDER, '**/*.mat'), recursive=True)
        txt_files = glob.glob(os.path.join(EXTRACT_FOLDER, '**/*.txt'), recursive=True)

        # Debugging: Log detected files
        print(f"MAT files: {mat_files}")
        print(f"TXT files: {txt_files}")

        # Ensure at least one .mat and .txt file is present
        if not mat_files or not txt_files:
            return jsonify({"error": "No .mat or .txt files found in the uploaded folder"}), 400

        # Pair .mat and .txt files
        mat_txt_pairs = []
        for mat_file in mat_files:
            txt_file = mat_file.replace('.mat', '_timePoints.txt')  # Assume matching naming convention
            if txt_file in txt_files:
                mat_txt_pairs.append((mat_file, txt_file))
            else:
                return jsonify({"error": f"Missing .txt file for {mat_file}"}), 400

        # Debugging: Log file pairs
        print(f"File pairs: {mat_txt_pairs}")

        # Process each .mat and .txt pair
        for mat_path, txt_path in mat_txt_pairs:
            try:

                channel_name = os.path.basename(mat_path).split('-')[0]
                mat_data = parse_mat_file(mat_path)
                print(len(mat_data['cycles']))
                print(mat_data['cycles'][0]['current_measurements'][41])
                #print(mat_data['cycles'][0]['current_measurements'])
                timepoints = parse_txt_file(txt_path)
                print(timepoints)
                insert_data(DB_PATH, mat_data, timepoints, experiment_name, channel_name)
            except Exception as e:
                return jsonify({"error": f"Error processing files {mat_path} and {txt_path}: {e}"}), 500

        # Populate the ProcessedData table
        try:
            populate_processed_data(DB_PATH)
            print("ProcessedData table populated successfully.")
        except Exception as e:
            return jsonify({"error": f"Error populating processed data: {e}"}), 500

        # Final success response
        return jsonify({"message": "Folder uploaded and processed successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500



if __name__ == '__main__':
    app.run(debug=True)
