import csv
import json


def save_acquisition_data_to_csv(json_data, csv_filename):
    # Parse the JSON data
    data = json.loads(json_data)

    # Extract xData and yData
    x_data = data['acquisition'][0]['roi'][0]['xData']
    y_data = data['acquisition'][0]['roi'][0]['yData'][0]  # Assuming yData is a list of lists

    # Write to CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['xData', 'yData'])  # Write headers
        for x, y in zip(x_data, y_data):
            writer.writerow([x, y])


# Example usage
json_data = '''{
    "acquisition": [{
        "acqIndex": 1,
        "roi": [{
            "roiIndex": 1,
            "xBinning": 1,
            "xData": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "xOrigin": 0,
            "xSize": 16,
            "yBinning": 4,
            "yData": [[602, 600, 600, 598, 599, 598, 598, 598, 597, 597, 598, 599, 599, 597, 600, 597]],
            "yOrigin": 0,
            "ySize": 4
        }]
    }],
    "timestamp": "2025.03.24 10:04:51.838"
}'''

save_acquisition_data_to_csv(json_data, 'acquisition_data.csv')
