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
  - View a pie chart that compares your total income versus total expenses, helping you visually analyze your financial health.

- **PDF Generation (optional)**:
  - Export your financial summaries to a PDF file for easy sharing or record-keeping (optional feature using either `fpdf` or `reportlab`).

## Update Description

In this update, we significantly enhanced the pie chart functionality by implementing a custom legend to ensure consistent and clear color representation for each category. The chart window size was increased and the layout was optimized to accommodate longer category names through text wrapping, improving readability. Additionally, we streamlined the chart rendering process to eliminate performance lag when toggling between different chart views. The application now dynamically resizes both the charts and legends in response to window adjustments, providing a more seamless and responsive user experience. These improvements collectively enhance the visual clarity and usability of the financial overview, making data analysis more efficient and intuitive.

## Technologies Used

- **Python**: The core programming language for developing the application.
- **Tkinter**: Python's built-in GUI library for creating a user-friendly desktop application.
- **Pandas**: For data manipulation and management of financial data.
- **Matplotlib**: For creating pie charts to visualize income vs. expenses.
- **Bcrypt**: To securely hash and manage user passwords.
- **SQLite**: (built-in) for storing and managing user and transaction data in a lightweight database.
- **FPDF**: (optional) for generating PDF reports of user financial summaries.
- **Pytest**: For writing unit tests to ensure the application functions as expected.
  
## How to Run the Project

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/finance-tracker.git
    ```

2. **Navigate to the Project Directory**:
    ```bash
    cd finance-tracker/src
    ```

3. **Install Required Packages**:
   
   Ensure you have `pip` installed, then run:
    ```bash
    pip install -r requirements.txt
    ```
   
   *If you don't have a `requirements.txt` file, you can install the packages individually:*
    ```bash
    pip install matplotlib pandas dateparser
    ```

4. **Run the Application**:
    ```bash
    python main.py
    ```

## Future Improvements

- **Enhanced Reports**: Option to export detailed reports as PDFs.
- **Additional Graphs**: Adding more charts for better financial insights (e.g., monthly expenses, category-based analysis).
- **Recurring Transactions**: Ability to add recurring transactions (rent, subscriptions, etc.).

Contributions are welcome! Feel free to open issues and submit pull requests to improve the project.
