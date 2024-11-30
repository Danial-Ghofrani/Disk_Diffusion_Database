Description
This repository contains a Python-based database management system for handling antibiotic resistance thresholds, inspired by the Clinical and Laboratory Standards Institute (CLSI) guidelines. The system uses MySQL to manage and query data about bacteria, antibiotics, and their associated resistance thresholds (Susceptible, Intermediate, Resistant, and Susceptible-Dose Dependent values).

Features
Database Creation and Connection: Automatically creates and connects to the MySQL database if it doesn't exist.
Resistance Threshold Classification: Classifies Minimum Inhibitory Concentration (MIC) values into categories (S, I, R, or SDD) based on provided thresholds.
Interactive Data Entry: Allows users to add new entries interactively, including susceptibility and resistance values.
Customizable Indications: Supports multiple indications for bacteria-antibiotic combinations, enabling granular MIC classification.
Data Management: Handles missing or optional values with appropriate defaults and validations.
Table Reindexing: Includes functionality to reindex the database table to fill ID gaps and ensure sequential ordering.
Preloaded Data: Contains over 300 manually entered rows of resistance thresholds for various bacteria and antibiotics, sourced directly from CLSI guidelines.

How to Use
Setup: Ensure you have a running MySQL server and update the db_info dictionary with your MySQL credentials.
Run the Script: Use the provided methods to interact with the database, classify MIC values, or add new entries.
Extend the Database: Insert additional rows or modify existing ones via the interactive data entry tool.
This tool is ideal for microbiologists, researchers, and clinicians who need an easy-to-use database for managing and analyzing antibiotic resistance data.

