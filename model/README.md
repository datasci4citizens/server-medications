# Model

Schemas and diagrams of the data model.

# Medication API

This API is designed to be consumed by a mobile application, helping elderly users and caregivers manage medications, diseases, and medication tracking records. Below are the specifications for each endpoint.

## Base URL
https://api.example.com/v1

## Endpoints

### Medication Users (MedicationUser)

#### **GET /medication-users**
- **Description**: Returns a list of all medication users.

#### **GET /medication-users/{id}**
- **Description**: Returns the details of a specific medication user.

#### **POST /medication-users**
- **Description**: Creates a new medication user.

#### **PUT /medication-users/{id}**
- **Description**: Updates the details of a medication user.

#### **DELETE /medication-users/{id}**
- **Description**: Deletes a medication user.

---

### Diseases (Disease)

#### **GET /diseases**
- **Description**: Returns a list of registered diseases.

---

### Medications (Drug)

#### **GET /drugs**
- **Description**: Returns a list of medications.

#### **GET /drugs/{id}**
- **Description**: Returns the details of a specific medication.

---

### Medication Tracking Records (TrackingRecords)

#### **POST /tracking-records**
- **Description**: Records the administration of a medication by a user.

---

### Drug Interactions (DrugInteraction)

#### **GET /drug-interactions**
- **Description**: Returns a list of all recorded drug interactions.

#### **GET /drug-interactions/{drug_a_id}/{drug_b_id}**
- **Description**: Returns the interaction details between two specific drugs.

### **GET /food-interactions/{drug_id}** 
- **Description**: Returns the interaction details between a specific drug and food items.