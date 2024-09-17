# Personal Finance Tracker

## Project Overview

Welcome to **Personal Finance Tracker**, a desktop-based finance management tool built using Python and Tkinter. This application allows users to manage their income, expenses, and overall finances in an intuitive and secure way. With additional features like chart visualization, financial summaries, and secure login/logout, this project aims to provide a personal, simple, yet robust solution to track finances.

## Features

- **User Authentication**: Secure user registration and login using password hashing with `bcrypt`. Each user has their own financial data, ensuring privacy and personalized data management.
  
- **Transaction Management**:
  - Add income or expense transactions.
  - Track various categories of expenses like "Daily", "Market", "Rent", "Utilities", etc.
  - Keep detailed records of each transaction with amounts, dates, and descriptions.
  
- **View Transactions**: 
  - View a list of all your transactions in a neatly formatted window, making it easy to browse through your financial history.

- **Delete Transactions**: 
  - Delete individual transactions easily from your transaction list, allowing full control over your financial data.

- **Financial Summary**:
  - Get an overview of your finances, including total income, total expenses, and remaining balance.
  
- **Chart Visualization**: 
  - View a bar chart that compares your total income versus total expenses, helping you visually analyze your financial health.

- **PDF Generation (optional)**:
  - Export your financial summaries to a PDF file for easy sharing or record-keeping (optional feature using either `fpdf` or `reportlab`).

## Technologies Used

- **Python**: The core programming language for developing the application.
- **Tkinter**: Python's built-in GUI library for creating a user-friendly desktop application.
- **Pandas**: For data manipulation and management of financial data.
- **Matplotlib**: For creating bar charts to visualize income vs. expenses.
- **Bcrypt**: To securely hash and manage user passwords.
- **SQLite**: (built-in) for storing and managing user and transaction data in a lightweight database.
- **FPDF**: (optional) for generating PDF reports of user financial summaries.
- **Pytest**: For writing unit tests to ensure the application functions as expected.
  
## How to Run the Project

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/finance-tracker.git

## Future Improvements
Enhanced Reports: Option to export detailed reports as PDFs.
Graphs: Adding more charts for better financial insights (e.g., monthly expenses, category-based analysis).
Recurring Transactions: Ability to add recurring transactions (rent, subscriptions, etc.).

##Contributions
Contributions are welcome! Feel free to open issues and submit pull requests to improve the project.

