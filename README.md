# Antibiotic Resistance Database Management System  

This repository contains a Python-based database management system designed to handle disk diffusion test antibiotic resistance thresholds, inspired by the **Clinical and Laboratory Standards Institute (CLSI)** guidelines. It leverages **MySQL** for storing and querying data on bacteria, antibiotics, and their associated resistance thresholds (Susceptible, Intermediate, Resistant, and Susceptible-Dose Dependent values).  

---

## Features  

1. **Database Creation and Connection**  
   - Automatically creates and connects to the MySQL database if it doesn’t exist.  

2. **Resistance Threshold Classification**  
   - Classifies Minimum Inhibitory Concentration (MIC) values into categories (`S`, `I`, `R`, or `SDD`) based on provided thresholds.  

3. **Interactive Data Entry**  
   - Allows users to add new entries interactively, including susceptibility and resistance values.  

4. **Customizable Indications**  
   - Supports multiple indications for bacteria-antibiotic combinations, enabling granular MIC classification.  

5. **Data Management**  
   - Handles missing or optional values with appropriate defaults and validations.  

6. **Table Reindexing**  
   - Includes functionality to reindex the database table to fill ID gaps and ensure sequential ordering.  

7. **Preloaded Data**  
   - Contains over 300 manually entered rows of resistance thresholds for various bacteria and antibiotics, sourced directly from **CLSI guidelines**.  

---

## How to Use  

1. **Setup**  
   - Ensure you have a running MySQL server.  
   - Update the `db_info` dictionary in the script with your MySQL credentials.  

2. **Run the Script**  
   - Use the provided methods to:  
     - Interact with the database.  
     - Classify MIC values.  
     - Add new entries interactively.  

3. **Extend the Database**  
   - Insert additional rows or modify existing ones using the interactive data entry tool.  

---

## Ideal For  

This tool is designed for **microbiologists**, **researchers**, and **clinicians** who need a robust yet easy-to-use database to manage and analyze antibiotic resistance data efficiently.  

---

## Requirements  

- Python 3.x  
- MySQL Server  
- Python libraries:  
  - `mysql-connector-python`  
  - `pandas`  
  - `matplotlib`  

---

## Acknowledgments  

The resistance thresholds and MIC classification standards are sourced from the **CLSI M100 guidelines**.  

---


