# Model

### Drug Tables

1. **DrugUse**
   - Records each drug that a user is actively or has historically used.
   - **Fields**:
     - `user_id`: References the user who is taking the drug.
     - `comercial_name_id`: References the commercial name of the drug.
     - `presentation_id`: References the specific presentation and dosage (e.g., tablet, capsule, 5mg).
     - `start_date` / `end_date`: Duration of drug usage.
     - `observation`: Additional notes.
     - `quantity`: Quantity of the drug.
     - `status`: Status of the drug use ("active" or "inactive").
   - **Relationships**:
     - Linked to `User`, `ComercialNames`, `Presentations`, and `Schedule` tables.

2. **ComercialNamesPresentations**
   - Represents the link between commercial names and drug presentations, allowing multiple presentations for each commercial name.
   - **Fields**:
     - `comercial_name_id`: Links to a specific commercial name.
     - `presentation_id`: Links to a specific presentation.

3. **Presentations**
   - Lists the various formats or presentations of drugs (e.g., tablet, injection).
   - **Fields**:
     - `value`: Description of the presentation format.
   - **Relationships**:
     - Connected to `ComercialNames` through `ComercialNamesPresentations`.
     - Linked to `DrugUse` for direct references to drug usage.

4. **ComercialNamesActivePrinciple**
   - Associates commercial drug names with active pharmaceutical ingredients.
   - **Fields**:
     - `active_principle_id`: References an active ingredient.
     - `comercial_name_id`: References a commercial drug name.

5. **ActivePrinciple**
   - Lists active ingredients in drugs.
   - **Fields**:
     - `code`: ANVISA's unique identifier for the active ingredient.
     - `active_ingredient`: Name of the active ingredient.
   - **Relationships**:
     - Connected to `ComercialNames` through `ComercialNamesActivePrinciple`.

6. **ComercialNames**
   - Contains the commercial names of drugs.
   - **Fields**:
     - `comercial_name`: Name under which the drug is sold.
   - **Relationships**:
     - Links to `DrugUse`, `Presentations`, and `ActivePrinciple` tables.

7. **Schedule**
   - Defines the medication schedule for users, indicating when they should take a drug.
   - **Fields**:
     - `drug_use_id`: Links to a specific drug use instance.
     - `type`: Type of schedule ("H" for Hour, "D" for Day).
     - `value`: Defines the specific time/day for medication.
   - **Relationships**:
     - Linked to `DrugUse` to provide a detailed schedule.

---

### User Tables

1. **UserCaretaker**
   - A linking table between users and their caretakers, allowing many-to-many relationships.
   - **Fields**:
     - `user_id`: References a specific user.
     - `caretaker_id`: References a specific caretaker.

2. **Caretaker**
   - Stores caretaker information.
   - **Fields**:
     - `name`: Caretaker's name.
     - `email`: Optional email address.
   - **Relationships**:
     - Connects with `User` through `UserCaretaker`.

3. **UserDisease**
   - Represents the relationship between users and diseases they are diagnosed with.
   - **Fields**:
     - `user_id`: References a specific user.
     - `disease_id`: References a specific disease.
     - `status`: Optional status of the disease (e.g., active, inactive).
   - **Relationships**:
     - Connects `User` and `Disease`.

4. **Disease**
   - Stores disease information relevant to users.
   - **Fields**:
     - `name`: Disease name.
     - `description`: Optional description.
   - **Relationships**:
     - Links to `User` through `UserDisease`.

5. **User**
   - Primary table for user data, holding personal and contact information.
   - **Fields**:
     - `name`, `email`: Basic identification fields.
     - `birth_date`: User's birth date.
     - `phone_number`: Contact number.
     - `emergency_contact_name` / `emergency_contact_number`: Emergency contact details.
     - `accept_tcle`: Consent for data sharing.
     - `scholarship`, `gender`, `sex`: Additional demographic information.
   - **Relationships**:
     - Linked to `Caretaker`, `UserDisease`, and `DrugUse` for complete user management.

---

# Medication API

This API is designed to be consumed by a mobile application, helping elderly users and caregivers manage medications, diseases, and medication tracking records. Below are the specifications for each endpoint.

## Base URL
https://api.example.com/v1

# Endpoints

## Users
#### **GET /users**
- Returns a list of all users.

#### **GET /users/{user_id}**
- Returns the details of a specific user.

#### **POST /users**
- Creates a new user.

#### **PUT /users/{user_id}**
- Updates the details of a user.

#### **DELETE /users/{user_id}**
- Deletes a user.


## Drugs
for the databese, each drug consists of a Comercial name that has the properties Active principles and Presentations. Whenever a Drug is linked to a User via the DrugUse table, the link is via Comercial name and Presentation.

### **GET /drugs/{user_id}/**
- Get all the drugs linked to a specific user

### **POST /drugs/{user_id}**
- Link user to a drug

### **GET /drugs/**
- Get all drugs

### **GET /drugs/drug_id**
- Get a specific drug

### **POST /drugs/deactivate/{user_id}/{drug_id}**
- Change the status of a DrugUse object to "deactivated" this is used instead of deleting the instance for research purposes

## Caretakers
The app is intended to be used either by caretakers or by the pacient directly, each pacient can be associated with multiple caretakers (either family members or actual caretakers) to manage the medications that pacient takes

#### **GET /caretaker**
- Returns a list of all users.

#### **POST /caretaker**
- Creates a new user.

#### **GET /caretaker/{caretaker_id}**
- Returns the details of a specific user.

#### **PUT /caretaker/{caretaker_id}**
- Updates the details of a user.

#### **DELETE /caretaker/{caretaker_id}**
- Deletes a user.

### **GET /caretaker/{user_id}/caretakers**
- Read all caretakers associated with a specific user

### **GET /caretaker/{user_id}/caretakers/{caretaker_id}**
- Link a caretaker to a user

## Schedule
We separate the list of medicine linked to a user to the schedule the user takes them in separate tables, Schedule stores what time of day and what days a week the users take the medicine

#### **GET /schedule/{user_id}/schedule**
- Returns a list of all schedules of a specific users.

#### **POST /schedule/{user_id}/schedule**
- Creates a new schedule for a user.

#### **PUT /schedule/{user_id}/schedule/{schedule_id}**
- Updates the details of a schedule.

#### **DELETE /schedule/{user_id}/schedule/{schedule_id}**
- Deletes a schedule.

## Diseases
Some interactions between diseases and medications are important for the research later on. 

#### **GET /diseases**
- Returns a list of registered diseases.

#### **POST /diseases**
- Creates a new diseases.

### **GET /diseases/{disease_id}** 
- Returns a specific diseases. 

#### **PUT /diseases/{disease_id}**
- Updates the details of a disease.

#### **DELETE /diseases/{disease_id}**
- Deletes a disease.

#### **POST /diseases/{user_id}/disease**
- Links a user to a disease.
---