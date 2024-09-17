import sys
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from models import user_model  # Import user_model
import dateparser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Ensure the project root directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FinanceTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Personal Finance Tracker")
        self.geometry("700x500")  # Increased the window size for better visibility
        self.configure(bg="#2b3e50")  # Dark-blue background for the main window

        # Initialize the database (create users and transactions table if it doesn't exist)
        user_model.create_users_table()
        user_model.create_transactions_table()  # Create the transactions table

        # By default, show the login window first
        self.show_login_window()

    def show_login_window(self):
        """Display the login window"""
        if hasattr(self, 'main_frame'):  # Check if the main frame exists and destroy it on logout
            self.main_frame.destroy()

        self.login_frame = LoginFrame(self)
        self.login_frame.pack(expand=True, fill="both")

    def show_main_window(self, user_id):
        """Display the main application window after successful login"""
        self.login_frame.destroy()  # Remove the login frame
        self.main_frame = MainApplication(self, user_id)  # Pass the user_id to the main window
        self.main_frame.pack(expand=True, fill="both")


class LoginFrame(tk.Frame):
    """Login and signup form"""
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.configure(bg="#2b3e50")  # Dark-blue background for the login frame

        self.grid_columnconfigure(0, weight=1)  # Make column 0 expandable
        self.grid_columnconfigure(1, weight=1)  # Make column 1 expandable

        # Login or Signup option (we will start with Login as default)
        self.is_login = True

        # Title Label
        self.title_label = tk.Label(self, text="Welcome to Finance Tracker", font=("Arial", 20), bg="#2b3e50", fg="white")
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # Username label and entry
        self.username_label = tk.Label(self, text="Username:", font=("Arial", 12), bg="#2b3e50", fg="white")
        self.username_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = tk.Entry(self, font=("Arial", 12), bd=2, relief="solid", width=30)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Password label and entry
        self.password_label = tk.Label(self, text="Password:", font=("Arial", 12), bg="#2b3e50", fg="white")
        self.password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.password_entry = tk.Entry(self, show="*", font=("Arial", 12), bd=2, relief="solid", width=30)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Login/Signup button
        self.submit_button = tk.Button(self, text="Login", font=("Arial", 12), bg="#4CAF50", fg="white", width=15,
                                       relief="raised", command=self.submit)
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=20)  # Removed "sticky" for a centered button

        # Toggle between Login/Signup
        self.toggle_button = tk.Button(self, text="Don't have an account? Signup", font=("Arial", 10), fg="#007BFF", 
                                       bg="#2b3e50", borderwidth=0, command=self.toggle_mode)
        self.toggle_button.grid(row=4, column=0, columnspan=2, pady=10)


    def toggle_mode(self):
        """Toggle between login and signup mode"""
        if self.is_login:
            self.submit_button.config(text="Signup", bg="#FFA500")  # Change button color for Signup
            self.toggle_button.config(text="Already have an account? Login")
            self.is_login = False
        else:
            self.submit_button.config(text="Login", bg="#4CAF50")  # Change back to Login button color
            self.toggle_button.config(text="Don't have an account? Signup")
            self.is_login = True

    def submit(self):
        """Handle login or signup actions"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if self.is_login:
            # Authenticate user during login and retrieve user_id
            user_id = user_model.authenticate_user(username, password)
            if user_id:
                #messagebox.showinfo("Success", "Login successful!")
                self.master.show_main_window(user_id)  # Pass the user_id to the main window
            else:
                messagebox.showerror("Error", "Invalid credentials.")
        else:
            # Create user during signup
            if user_model.create_user(username, password):
                messagebox.showinfo("Success", "Account created! Please login.")
                self.toggle_mode()  # Switch back to login mode after signup
            else:
                messagebox.showerror("Error", "Username already exists.")


class MainApplication(tk.Frame):
    """Main dashboard and transaction management"""
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id  # Store the logged-in user's ID
        self.configure(bg="#2b3e50")  # Dark-blue background for the main application frame

        # Create a welcome label
        welcome_label = tk.Label(self, text="Welcome to the Personal Finance Tracker Dashboard!", font=("Arial", 16),
                                 bg="#2b3e50", fg="white")
        welcome_label.pack(pady=20)

        # Form to add a new transaction
        self.create_transaction_form()

        # Button frame for add, view, delete, and show chart buttons
        button_frame = tk.Frame(self, bg="#2b3e50")
        button_frame.pack(pady=10)

        # Add Transaction button
        add_transaction_button = tk.Button(button_frame, text="Add Transaction", font=("Arial", 12), bg="#FFA500", fg="white", 
                                           width=15, relief="raised", command=self.add_transaction)
        add_transaction_button.grid(row=0, column=0, padx=10)

        # Delete Transaction button
        delete_transaction_button = tk.Button(button_frame, text="Delete Transaction", font=("Arial", 12), bg="#FF4500", fg="white", 
                                              width=15, relief="raised", command=self.delete_transaction)
        delete_transaction_button.grid(row=0, column=1, padx=10)

        # View Transactions button
        view_transactions_button = tk.Button(button_frame, text="View Transactions", font=("Arial", 12), bg="#4CAF50", fg="white", 
                                             width=15, relief="raised", command=self.view_transactions)
        view_transactions_button.grid(row=0, column=2, padx=10)

        # Logout button at the bottom right
        logout_button = tk.Button(self, text="Logout", font=("Arial", 12), bg="#FF0000", fg="white", 
                                  width=10, command=self.logout)
        logout_button.place(relx=0.95, rely=0.95, anchor="se")  # Place in the bottom-right corner

        # Summary button at the bottom-left
        summary_button = tk.Button(self, text="Summary", font=("Arial", 12), bg="#00CED1", fg="white",
                                   width=15, relief="raised", command=self.show_summary)
        summary_button.place(relx=0.05, rely=0.95, anchor="sw")  # Place in the left-bottom corner

        # Show Chart button in between Summary and Logout
        chart_button = tk.Button(self, text="Show Chart", font=("Arial", 12), bg="#FFD700", fg="white", 
                                 width=15, relief="raised", command=self.show_chart)
        chart_button.place(relx=0.50, rely=0.95, anchor="s")  # Place in between Summary and Logout

    def show_chart(self):
        """Display a bar chart of income vs expenses"""
        total_income, total_expenses = user_model.get_financial_summary(self.user_id)

        # Create a figure for the chart
        fig, ax = plt.subplots(figsize=(5, 4))

        # Bar chart data
        labels = ['Income', 'Expenses']
        values = [total_income, total_expenses]

        # Create the bar chart
        ax.bar(labels, values, color=['green', 'red'])
        ax.set_ylabel('Amount ($)')
        ax.set_title('Income vs Expenses')

        # Create a window for the chart
        chart_window = tk.Toplevel(self)
        chart_window.title("Income vs Expenses Chart")
        chart_window.geometry("500x400")

        # Add the chart to the window using Tkinter's canvas
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def logout(self):
        """Handle logout and return to login screen"""
        self.master.show_login_window()

    def create_transaction_form(self):
        """Create the form to add a new transaction"""
        form_frame = tk.Frame(self, bg="#2b3e50")
        form_frame.pack(pady=20)

        # Amount
        tk.Label(form_frame, text="Amount:", bg="#2b3e50", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.amount_spinbox = tk.Spinbox(form_frame, from_=0.0, to=10000.0, increment=1.0, font=("Arial", 12), width=20)
        self.amount_spinbox.grid(row=0, column=1, padx=10, pady=5)

        # Category
        tk.Label(form_frame, text="Category:", bg="#2b3e50", fg="white", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.category_var = tk.StringVar()
        self.category_var.set("Daily")  # Set default value
        self.category_menu = tk.OptionMenu(form_frame, self.category_var, "Daily", "Market", "Others", "Rent", "Utilities")
        self.category_menu.grid(row=1, column=1, padx=10, pady=5)

        # Type
        tk.Label(form_frame, text="Type:", bg="#2b3e50", fg="white", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.type_var = tk.StringVar()
        self.type_var.set("Expense")  # Set default value
        self.type_menu = tk.OptionMenu(form_frame, self.type_var, "Income", "Expense")
        self.type_menu.grid(row=2, column=1, padx=10, pady=5)

        # Date
        tk.Label(form_frame, text="Date:", bg="#2b3e50", fg="white", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = tk.Entry(form_frame, width=20, font=("Arial", 12))
        self.date_entry.grid(row=3, column=1, padx=10, pady=5)

        # Description
        tk.Label(form_frame, text="Description:", bg="#2b3e50", fg="white", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.description_text = tk.Text(form_frame, width=20, height=4, font=("Arial", 12))
        self.description_text.grid(row=4, column=1, padx=10, pady=5)

    def add_transaction(self):
        """Handle adding a new transaction"""
        amount = float(self.amount_spinbox.get())
        category = self.category_var.get()
        transaction_type = self.type_var.get().lower()  # Either 'income' or 'expense'
        date_input = self.date_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()

        # Convert natural language date to YYYY-MM-DD
        parsed_date = dateparser.parse(date_input)
        if parsed_date:
            date = parsed_date.strftime("%Y-%m-%d")
        else:
            messagebox.showerror("Error", "Invalid date format. Please try again.")
            return

        # Use the logged-in user's ID (self.user_id)
        user_model.add_transaction(self.user_id, amount, category, transaction_type, date, description)
        messagebox.showinfo("Success", "Transaction added successfully!")

        # Clear the form fields after adding a transaction
        self.clear_form()

        # Refresh the financial summary after adding a transaction
        self.refresh_financial_summary()

    def clear_form(self):
        """Clear the form fields after a transaction is added"""
        self.amount_spinbox.delete(0, "end")
        self.amount_spinbox.insert(0, "0")
        self.category_var.set("Daily")
        self.type_var.set("Expense")
        self.date_entry.delete(0, "end")
        self.description_text.delete("1.0", "end")

    def delete_transaction(self):
        """Display a list of transactions with delete options"""
        transactions = user_model.get_transactions(self.user_id)

        if not transactions:
            messagebox.showinfo("No Transactions", "No transactions to delete.")
            return

        delete_window = tk.Toplevel(self)
        delete_window.title("Delete Transaction")
        delete_window.geometry("600x400")

        # Create a list of transactions with delete buttons
        for idx, transaction in enumerate(transactions):
            # Display transaction details
            tk.Label(delete_window, text=f"Transaction {idx + 1}:", font=("Arial", 12)).grid(row=idx, column=0, padx=10, pady=5)
            tk.Label(delete_window, text=f"Amount: {transaction[2]}", font=("Arial", 10)).grid(row=idx, column=1)
            tk.Label(delete_window, text=f"Category: {transaction[3]}", font=("Arial", 10)).grid(row=idx, column=2)
            tk.Label(delete_window, text=f"Type: {transaction[4]}", font=("Arial", 10)).grid(row=idx, column=3)
            tk.Label(delete_window, text=f"Date: {transaction[5]}", font=("Arial", 10)).grid(row=idx, column=4)

            # Add a delete button for each transaction
            delete_button = tk.Button(delete_window, text="Delete", font=("Arial", 10), bg="#FF4500", fg="white",
                                      command=lambda t_id=transaction[0]: self.confirm_delete(t_id, delete_window))
            delete_button.grid(row=idx, column=5, padx=10, pady=5)

    def confirm_delete(self, transaction_id, delete_window):
        """Confirm and delete the transaction"""
        result = messagebox.askyesno("Delete Transaction", "Are you sure you want to delete this transaction?")
        if result:
            # Delete the transaction from the database
            user_model.delete_transaction(transaction_id)
            messagebox.showinfo("Deleted", "Transaction deleted successfully.")
            delete_window.destroy()  # Close the delete window
            self.refresh_financial_summary()  # Refresh the summary after deletion


    def view_transactions(self):
        """Display a list of transactions for the logged-in user"""
        transactions = user_model.get_transactions(self.user_id)  # Replace with the actual logged-in user ID

        # Create a new window to show the transactions
        view_window = tk.Toplevel(self)
        view_window.title("View Transactions")
        view_window.geometry("600x400")

        # Create a label to display each transaction
        for idx, transaction in enumerate(transactions):
            tk.Label(view_window, text=f"Transaction {idx+1}:", font=("Arial", 12)).pack(pady=5)
            tk.Label(view_window, text=f"Amount: {transaction[2]}", font=("Arial", 10)).pack()
            tk.Label(view_window, text=f"Category: {transaction[3]}", font=("Arial", 10)).pack()
            tk.Label(view_window, text=f"Type: {transaction[4]}", font=("Arial", 10)).pack()
            tk.Label(view_window, text=f"Date: {transaction[5]}", font=("Arial", 10)).pack()
            tk.Label(view_window, text=f"Description: {transaction[6]}", font=("Arial", 10)).pack()
            tk.Label(view_window, text="----------------------", font=("Arial", 10)).pack(pady=5)

    def show_summary(self):
        """Display a summary of income, expenses, and remaining balance"""
        total_income, total_expenses = user_model.get_financial_summary(self.user_id)
        remaining_balance = total_income - total_expenses

        summary_window = tk.Toplevel(self)
        summary_window.title("Financial Summary")
        summary_window.geometry("400x200")

        # Display summary information
        tk.Label(summary_window, text=f"Total Income: ${total_income}", font=("Arial", 14)).pack(pady=10)
        tk.Label(summary_window, text=f"Total Expenses: ${total_expenses}", font=("Arial", 14)).pack(pady=10)
        tk.Label(summary_window, text=f"Remaining Balance: ${remaining_balance}", font=("Arial", 14)).pack(pady=10)


if __name__ == "__main__":
    app = FinanceTrackerApp()
    app.mainloop()
