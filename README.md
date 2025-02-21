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

