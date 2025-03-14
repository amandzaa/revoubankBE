# User Authentication & Transaction Handling Flowchart

## Overview

This document provides a comprehensive representation of the **User Authentication** and **Transaction Handling** processes. It details each step involved in authentication, error handling, security measures, and transaction workflows to ensure a structured and secure system implementation.

## Sections

The flowchart consists of two major parts:

1. **User Authentication**
   - Login Process
   - User Registration Process
   - Security Code Verification
2. **Transaction Handling**
   - Transaction Initialization
   - Withdrawal Process
   - Deposit Process
   - Funds Transfer Process

---

## 1. User Authentication

User authentication ensures secure access to the system by verifying user credentials and handling failed login attempts. It includes the **Login**, **Registration**, and **Security Code Verification** processes.

![User Authentication Flowchart](assets/user_authentification.drawio.png)

### **1.1 Login Process**

1. The user enters credentials (**username & password**).
2. The system validates the input format:
   - If the format is invalid → **Error Message Displayed**
   - If valid → Proceed to the next step
3. The system queries the database to check if the user exists:
   - If the user does not exist → Offer **Registration Option**
   - If the user exists → Proceed to password verification
4. The system verifies the entered password:
   - If correct → **Login Successful**
   - If incorrect → Increment failed attempts
5. If failed attempts exceed the allowed limit:
   - Lock the account
   - Display **Account Locked Message**
6. If login is successful:
   - Redirect the user to the **Dashboard**

### **1.2 User Registration Process**

1. The user provides the required registration details:
   - Username
   - Email
   - Password & Confirm Password
2. The system validates the input details:
   - If invalid → **Show Validation Error**
   - If valid → Proceed with registration
3. The system creates an account and sends a verification email.
4. The user verifies the email:
   - If verified → Registration is completed
   - If not → The system waits for verification before proceeding

### **1.3 Security Code Verification**

1. The system generates a **security code** and sends it via **SMS/Email**.
2. The user enters the security code.
3. The system verifies the code:
   - If valid → **Generate Authentication Token & Store it**
   - If invalid → **Display Invalid Code Error**
4. Upon successful verification, the user is redirected to the dashboard.

---

## 2. Transaction Handling

The transaction handling system manages user-initiated financial transactions, including deposits, withdrawals, and transfers.

![Transaction Handling Flowchart](assets/transaction_handling.drawio.png)

### **2.1 Transaction Initialization**

1. The user selects a transaction type:
   - **Withdrawal**
   - **Deposit**
   - **Funds Transfer**
2. Based on the selection, the system processes the request accordingly.

### **2.2 Withdrawal Process**

1. The user selects a withdrawal method:
   - **Bank Branch** → Enter branch withdrawal details
   - **ATM** → Enter ATM withdrawal details
2. The user selects an account balance.
3. The user enters the withdrawal amount.
4. The system validates the input fields:
   - If invalid → **Show Error Message**
   - If insufficient funds → **Show Insufficient Funds Error**
5. If valid, the system:
   - Processes the transaction
   - Updates the account balance
   - Records the transaction in the transaction history

### **2.3 Deposit Process**

1. The user selects a deposit method:
   - **Direct Deposit** → Enter direct deposit details
   - **Check Deposit** → Enter check details
   - **Cash Deposit** → Enter cash amount
2. The user selects an account balance.
3. The system validates deposit details:
   - If invalid → **Show Error Message**
4. If valid, the system:
   - Processes the deposit
   - Updates the account balance
   - Records the transaction in the transaction history

### **2.4 Funds Transfer Process**

1. The user selects a payer account.
2. The system displays account balance and IBAN.
3. The user selects a transfer type:
   - **Own Account Transfer**
   - **Other Account Transfer**
4. If transferring to another account:
   - Enter beneficiary details
   - Choose from **Saved Beneficiaries** or **New Beneficiary**
5. The user fills in the required fields:
   - Amount
   - Date
   - Transfer Purpose
   - Beneficiary Name & Email
   - Payer’s Reference
6. The system validates input details:
   - If invalid → **Show Error Message**
7. If valid, the system:
   - Confirms transaction details
   - Processes the transaction
   - Updates account balance
   - Records the transaction history
8. The system updates:
   - **Transaction View**: Filter by type, search function, pending transactions
   - **Statistics**: Weekly spending overview & transaction timeline
9. A transaction receipt is generated.
10. The transaction is marked as **Complete**.

---

## Flowchart Legend

- **Oval:** Start/End points.
- **Diamond:** Decision-making processes.
- **Rectangle:** Processing steps.
- **Parallelogram:** Input/Output operations.
- **Arrows:** Flow direction of the process.

---

## Usage

This flowchart serves as a guide for **developers, system architects, and financial analysts** implementing user authentication and transaction handling systems. It ensures a well-structured approach to login attempts, security verifications, and financial transactions.

---

## File Information

- **User Authentication Flowchart:** `assets/user_authentification.drawio.png`
- **Transaction Handling Flowchart:** `assets/transaction_handling.drawio.png`
- **Format:** PNG image
- **Tool Used:** Draw.io

For any modifications, use **Draw.io** or a compatible flowcharting tool to update the diagrams accordingly.

# RevoBank API

A RESTful API for a banking application that provides secure and efficient interaction between users and the system.

## Overview

RevoBank API serves as the backbone for the RevoBank application, implementing core features for User Management, Account Management, and Transaction Management. The API follows RESTful principles and includes robust authentication and authorization mechanisms.

## Features

- **User Management**

  - User registration
  - User authentication with JWT
  - User profile management

- **Account Management**

  - Create bank accounts
  - View account details
  - Update account information
  - Delete accounts

- **Transaction Management**

  - Perform deposits, withdrawals, and transfers
  - View transaction history
  - Filter transactions by account, user_id

- **Security Features**
  - JWT-based authentication
  - Role-based authorization
  - Password hashing
  - Account ownership validation

## Technologies Used

- **Backend**: Python, Flask
- **Database**: SQLite (dummy database for demonstration)
- **Authentication**: JWT (JSON Web Tokens)

## Installation and Setup

### Prerequisites

- Python 3.11
- pip (Python package installer) or uv (faster package manager)

### Local Setup

1. Clone the repository:

   ```
   git clone https://github.com/revou-fsse-oct24/milestone-3-amandzaa.git
   cd milestone-3-amandzaa
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

The API will be available at `http://127.0.0.1:5000/`.

## API Documentation

Full API documentation is available at: [Postman Documentation RevouBank](https://documenter.getpostman.com/view/42844883/2sAYkBrfo6)

### Authentication

#### Login

```
POST /login
```

**Request Body**:

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response**:

```json
{
  "message": "Login successful!",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMGU4OTYwYWUtZWY0Ny00ZGU4LThiNjAtOWE4MWIzYjU2OGVhIiwiZXhwIjoxNzQxOTYyNzA2fQ.QjHE6i7YUUZR8WY76GtFinlKfPFIWfKHMml7j38JMf0",
  "user": {
    "id": "0e8960ae-ef47-4de8-8b60-9a81b3b568ea"
  }
}
```

**For all authenticated endpoints, include the JWT token in the Authorization header**:

```
Authorization: Bearer {your_token}
```

### User Management

#### Create User

```
POST /users
```

**Request Body**:

```json
{
  "email": "amandappp@gmail.com",
  "name": "amd",
  "phone": "+222577764",
  "password": "B12345678"
}
```

**Response**:

```json
{
  "message": "User registered successfully!",
  "user_data": {
    "email": "amandappp@gmail.com",
    "name": "amd",
    "phone": "+222577764"
  },
  "user_id": "39730052-9dc8-46b0-b5df-65ee3afbd267"
}
```

#### Get All User Profile

```
GET /users/all
```

**Response**:

```json
{
  "users": [
    {
      "email": "john@example.com",
      "id": "0e8960ae-ef47-4de8-8b60-9a81b3b568ea",
      "name": "John Doe"
    },
    {
      "email": "amandaaaa@example.com",
      "id": "052f24bb-c03f-4060-9649-6276c9a15b59",
      "name": "amd aaa"
    },
    {
      "email": "tets@example.com",
      "id": "ee925f7d-f872-4b7d-8208-87e92ad26bdd",
      "name": "cacaca aaa"
    },
    {
      "email": "amanda@example.com",
      "id": "1fb14166-66d0-4c37-9ccb-fb333ee0a62a",
      "name": "cacaca aaa"
    },
    {
      "email": "amandappp@gmail.com",
      "id": "39730052-9dc8-46b0-b5df-65ee3afbd267",
      "name": "amd"
    }
  ]
}
```

#### Update User Profile

```
PUT /users/{id]
```

**Request Body**:

```json
{
  "email": "akiki@gmail.com",
  "name": "amd aaa",
  "phone": "+2255427774"
}
```

**Response**:

```json
{
  "changes": {
    "email": {
      "from": "john@example.com",
      "to": "akiki@gmail.com"
    },
    "name": {
      "from": "John Doe",
      "to": "amd aaa"
    },
    "phone": {
      "from": "+1234567890",
      "to": "+2255427774"
    }
  },
  "message": "Profile updated successfully!",
  "user_id": "0e8960ae-ef47-4de8-8b60-9a81b3b568ea"
}
```

### Account Management

#### Get All Accounts

```
GET /accounts/all
```

**Response**:

```json
[
  [
    {
      "account_name": "Primary Checking",
      "account_type": "checking",
      "balance": 5000,
      "created_at": "Fri, 14 Mar 2025 08:11:49 GMT",
      "currency": "USD",
      "id": "86622726-39b0-4c99-90ab-482e0cd59557",
      "status": "active",
      "updated_at": null,
      "user_id": "0e8960ae-ef47-4de8-8b60-9a81b3b568ea"
    },
    {
      "account_name": "Savings",
      "account_type": "savings",
      "balance": 10000,
      "created_at": "Fri, 14 Mar 2025 08:11:49 GMT",
      "currency": "USD",
      "id": "79cc4c03-7474-4bec-a639-2d96a493b04c",
      "status": "active",
      "updated_at": null,
      "user_id": "0e8960ae-ef47-4de8-8b60-9a81b3b568ea"
    },
    {
      "account_name": "Primary Checking",
      "account_type": "checking",
      "balance": 5000,
      "created_at": "Fri, 14 Mar 2025 08:11:49 GMT",
      "currency": "USD",
      "id": "cb6e53ac-7d1f-4bdd-b553-14145dbca0e0",
      "status": "active",
      "updated_at": null,
      "user_id": "052f24bb-c03f-4060-9649-6276c9a15b59"
    },
    {
      "account_name": "Tabungan kocheng guwee",
      "account_type": "savings",
      "balance": 10000,
      "created_at": "Fri, 14 Mar 2025 08:11:49 GMT",
      "currency": "USD",
      "id": "c8e2903a-359e-402d-9f4e-644f04bfd0df",
      "status": "active",
      "updated_at": "Fri, 14 Mar 2025 14:20:36 GMT",
      "user_id": "052f24bb-c03f-4060-9649-6276c9a15b59"
    },
    {
      "account_name": "Tabungan naik pesiar",
      "account_type": "savings",
      "balance": 0,
      "created_at": "Fri, 14 Mar 2025 14:21:59 GMT",
      "currency": "USD",
      "id": "fd2ff7ce-ed6c-4096-8923-9cee73691e12",
      "status": "active",
      "updated_at": "Fri, 14 Mar 2025 14:21:59 GMT",
      "user_id": "ee925f7d-f872-4b7d-8208-87e92ad26bdd"
    },
    {
      "account_name": "Tabungan nanas guwee",
      "account_type": "savings",
      "balance": 230,
      "created_at": "Fri, 14 Mar 2025 15:39:16 GMT",
      "currency": "USD",
      "id": "5fccd3a6-4b25-4b02-9ac6-1cf04d2e0281",
      "status": "active",
      "updated_at": "Fri, 14 Mar 2025 18:48:59 GMT",
      "user_id": "1fb14166-66d0-4c37-9ccb-fb333ee0a62a"
    }
  ]
]
```

#### Get Specific Account

```
GET /accounts/{account_id}
```

**Response**:

```json
{
  "account_name": "Tabungan kocheng guwee",
  "account_type": "savings",
  "balance": 10000,
  "created_at": "Fri, 14 Mar 2025 08:11:49 GMT",
  "currency": "USD",
  "id": "c8e2903a-359e-402d-9f4e-644f04bfd0df",
  "status": "active",
  "updated_at": "Fri, 14 Mar 2025 14:20:36 GMT",
  "user_id": "052f24bb-c03f-4060-9649-6276c9a15b59"
}
```

#### Create Account

```
POST /accounts
```

**Request Body**:

```json
{
  "account_name": "Tabungan bebek dan kuciing",
  "account_type": "savings",
  "currency": "USD"
}
```

**Response**:

```json
{
  "account_id": "482e0d75-213f-4a1e-8f21-e9795a96dd3f",
  "message": "Account created successfully!"
}
```

#### Update Account

```
PUT /accounts/{account_id}
```

**Request Body**:

```json
{
  "account_name": "Tabungan jalan jalan",
  "account_type": "deposit"
}
```

**Response**:

```json
{
  "message": "Account updated successfully!"
}
```

#### Delete Account

```
DELETE /accounts/{account_id}
```

**Response**:

```json
{
  "message": "Account deleted successfully"
}
```

### Transaction Management

#### Get Transactions

```
GET /transactions/all
```

**Optional Query Parameters**:

- `account_id`: Filter by specific account

**Response**:

```json
[
  {
    "account_id": "86622726-39b0-4c99-90ab-482e0cd59557",
    "amount": 1000,
    "description": "Initial deposit",
    "id": "b4421a14-134e-46b0-af7a-1ab7595e4cf6",
    "linked_transaction_id": null,
    "transaction_date": "Wed, 12 Feb 2025 08:11:49 GMT",
    "transaction_type": "deposit"
  },
  {
    "account_id": "86622726-39b0-4c99-90ab-482e0cd59557",
    "amount": 200,
    "description": "ATM withdrawal",
    "id": "874c525e-c11c-4a8a-bdea-719432663bcb",
    "linked_transaction_id": null,
    "transaction_date": "Thu, 27 Feb 2025 08:11:49 GMT",
    "transaction_type": "withdrawal"
  },
  {
    "account_id": "79cc4c03-7474-4bec-a639-2d96a493b04c",
    "amount": 1000,
    "description": "Initial deposit",
    "id": "865bd49b-9ebe-43cc-9b8e-2c0431818857",
    "linked_transaction_id": null,
    "transaction_date": "Wed, 12 Feb 2025 08:11:49 GMT",
    "transaction_type": "deposit"
  },
  {
    "account_id": "79cc4c03-7474-4bec-a639-2d96a493b04c",
    "amount": 200,
    "description": "ATM withdrawal",
    "id": "d665bfa7-f427-41f5-b3a9-9b2ecfef9d69",
    "linked_transaction_id": null,
    "transaction_date": "Thu, 27 Feb 2025 08:11:49 GMT",
    "transaction_type": "withdrawal"
  },
  {
    "account_id": "cb6e53ac-7d1f-4bdd-b553-14145dbca0e0",
    "amount": 1000,
    "description": "Initial deposit",
    "id": "f234ceaa-8ea2-4af9-b468-187720fca808",
    "linked_transaction_id": null,
    "transaction_date": "Wed, 12 Feb 2025 08:11:49 GMT",
    "transaction_type": "deposit"
  },
  {
    "account_id": "cb6e53ac-7d1f-4bdd-b553-14145dbca0e0",
    "amount": 200,
    "description": "ATM withdrawal",
    "id": "bdd36225-dba3-470a-9a00-893f1815642e",
    "linked_transaction_id": null,
    "transaction_date": "Thu, 27 Feb 2025 08:11:49 GMT",
    "transaction_type": "withdrawal"
  },
  {
    "account_id": "c8e2903a-359e-402d-9f4e-644f04bfd0df",
    "amount": 1000,
    "description": "Initial deposit",
    "id": "587369d1-b3a1-42b7-88c6-859e7f874f8e",
    "linked_transaction_id": null,
    "transaction_date": "Wed, 12 Feb 2025 08:11:49 GMT",
    "transaction_type": "deposit"
  },
  {
    "account_id": "c8e2903a-359e-402d-9f4e-644f04bfd0df",
    "amount": 200,
    "description": "ATM withdrawal",
    "id": "7c048701-4253-414e-a422-1cb95b318bd0",
    "linked_transaction_id": null,
    "transaction_date": "Thu, 27 Feb 2025 08:11:49 GMT",
    "transaction_type": "withdrawal"
  },
  {
    "account_id": "86622726-39b0-4c99-90ab-482e0cd59557",
    "amount": 500,
    "description": "Transfer to savings",
    "id": "50b15bbf-e3f0-4053-8e15-3026d60f18ba",
    "linked_transaction_id": "8920ef51-5973-4793-9488-036f9ae1fef5",
    "transaction_date": "Fri, 07 Mar 2025 08:11:49 GMT",
    "transaction_type": "transfer"
  },
  {
    "account_id": "79cc4c03-7474-4bec-a639-2d96a493b04c",
    "amount": 500,
    "description": "Transfer from checking",
    "id": "8920ef51-5973-4793-9488-036f9ae1fef5",
    "linked_transaction_id": "50b15bbf-e3f0-4053-8e15-3026d60f18ba",
    "transaction_date": "Fri, 07 Mar 2025 08:11:49 GMT",
    "transaction_type": "deposit"
  },
  {
    "account_id": "5fccd3a6-4b25-4b02-9ac6-1cf04d2e0281",
    "amount": 230,
    "description": "nabung",
    "id": "efa6b982-665f-48e0-85ae-e9eb221299bc",
    "linked_transaction_id": null,
    "transaction_date": "Fri, 14 Mar 2025 19:17:18 GMT",
    "transaction_type": "deposit"
  }
]
```

#### Get Transaction Details

```
GET /transactions/{transaction_id}
```

**Response**:

```json
{
  "account_id": "79cc4c03-7474-4bec-a639-2d96a493b04c",
  "amount": 500,
  "description": "Transfer from checking",
  "id": "8920ef51-5973-4793-9488-036f9ae1fef5",
  "linked_transaction_id": "50b15bbf-e3f0-4053-8e15-3026d60f18ba",
  "transaction_date": "Fri, 07 Mar 2025 08:11:49 GMT",
  "transaction_type": "deposit"
}
```

## Error Codes

The API uses HTTP status codes to indicate success or failure:

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: User not authorized to access resource
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server-side error

## Notes for Production

For a production environment, consider these enhancements:

1. Use a more robust database system (PostgreSQL, MySQL)
2. Implement HTTPS
3. Add rate limiting
4. Implement more comprehensive logging
5. Add monitoring and alerting
6. Set up database migrations
7. Implement automated testing
