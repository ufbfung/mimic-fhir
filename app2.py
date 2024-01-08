# -*- coding: utf-8 -*-
"""mimic on fhir web app.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SDk3n-hNh-G1jBHXWHX5UoxkHfJb_KcV
"""

import streamlit as st
import pandas as pd
import json
import requests

# Function to parse a single patient record from FHIR format
def parse_patient_record(record):
    patient_data = {
        'id': record['id'],
        'gender': record['gender'],
        'birthDate': record['birthDate'],
        'maritalStatus': record.get('maritalStatus', {}).get('coding', [{}])[0].get('code', None),
        'race': None,
        'ethnicity': None,
        'birthSex': None
    }

    # Parsing extensions for race, ethnicity, and birthSex
    for extension in record.get('extension', []):
        if extension['url'] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race':
            patient_data['race'] = extension['extension'][0]['valueCoding']['display']
        elif extension['url'] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity':
            patient_data['ethnicity'] = extension['extension'][0]['valueCoding']['display']
        elif extension['url'] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex':
            patient_data['birthSex'] = extension['valueCode']

    return patient_data

# Function to download a file from Google Drive
def download_file_from_google_drive(file_id):
    base_url = "https://drive.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(base_url, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(base_url, params=params, stream=True)

    return response.content.decode('utf-8')

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

# Load data
def load_data():
    pat_file_id = '1SxaVQAAjWzJPST4z0qkq-LRlx2xzQbDw'
    patient_data_content = download_file_from_google_drive(pat_file_id)
    patient_records = [parse_patient_record(json.loads(line)) for line in patient_data_content.splitlines()]
    return pd.DataFrame(patient_records)

# Streamlit app
def main():
    st.title("MIMIC on FHIR Data Explorer")
    st.write("Explore MIMIC on FHIR patient data.")

    # Load data
    patient_df = load_data()

    # Gender filter
    gender = st.radio("Select Gender:", ('All', 'Male', 'Female'))
    if gender != 'All':
        filtered_df = patient_df[patient_df['gender'] == gender.lower()]
    else:
        filtered_df = patient_df

    # Display patient data
    st.dataframe(filtered_df)

if __name__ == "__main__":
    main()