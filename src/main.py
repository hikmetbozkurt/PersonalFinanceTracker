# main.py

import sys
import os
import textwrap
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog  # Dosya diyaloğu için
from models import user_model  # Import user_model
import dateparser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd  # Excel için pandas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas  # PDF için
from reportlab.lib.utils import simpleSplit  # Metin sarmak için
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from reportlab.platypus.tables import Table, TableStyle

# Ensure the project root directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FinanceTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Personal Finance Tracker")
        self.geometry("900x700")
        self.resizable(False, False)  # Prevent resizing the window  # Pencere boyutunu büyüttük

        # Apply a modern theme
        style = ttk.Style(self)
        style.theme_use('clam')  # You can choose 'clam', 'alt', 'default', 'classic'

        # Customize button styles
        style.configure('TButton', background='#5DADE2', foreground='white', font=('Arial', 12))
        style.map('TButton', background=[('active', '#3498DB')])

        # Initialize the database
        user_model.create_users_table()
        user_model.create_transactions_table()
        user_model.create_categories_table()
        user_model.create_tags_table()
        user_model.create_transaction_tags_table()

        # Show the login window first
        self.show_login_window()

    def show_login_window(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()

        self.login_frame = LoginFrame(self)
        self.login_frame.pack(expand=True, fill="both")

    def show_main_window(self, user_id):
        self.login_frame.destroy()
        self.main_frame = MainApplication(self, user_id)
        self.main_frame.pack(expand=True, fill="both")

class LoginFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.is_login = True

        # Title Label
        self.title_label = ttk.Label(self, text="Welcome to Finance Tracker", font=("Arial", 20))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # Username label and entry
        self.username_label = ttk.Label(self, text="Username:", font=("Arial", 12))
        self.username_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = ttk.Entry(self, font=("Arial", 12), width=30)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Password label and entry
        self.password_label = ttk.Label(self, text="Password:", font=("Arial", 12))
        self.password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.password_entry = ttk.Entry(self, show="*", font=("Arial", 12), width=30)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Login/Signup button
        self.submit_button = ttk.Button(self, text="Login", command=self.submit)
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=20)
        # Bind Enter key to the login button
        self.master.bind("<Return>", lambda event: self.submit_button.invoke())

        # Toggle between Login/Signup
        self.toggle_button = ttk.Button(self, text="Don't have an account? Signup", command=self.toggle_mode)
        self.toggle_button.grid(row=4, column=0, columnspan=2, pady=10)

    def toggle_mode(self):
        if self.is_login:
            self.submit_button.config(text="Signup")
            self.toggle_button.config(text="Already have an account? Login")
            self.is_login = False
        else:
            self.submit_button.config(text="Login")
            self.toggle_button.config(text="Don't have an account? Signup")
            self.is_login = True

    def submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if self.is_login:
            user_id = user_model.authenticate_user(username, password)
            if user_id:
                self.master.show_main_window(user_id)
            else:
                messagebox.showerror("Error", "Invalid credentials.")
        else:
            if user_model.create_user(username, password):
                messagebox.showinfo("Success", "Account created! Please login.")
                self.toggle_mode()
            else:
                messagebox.showerror("Error", "Username already exists.")

class MainApplication(ttk.Frame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id

        # Create a welcome label
        welcome_label = ttk.Label(self, text="Welcome to the Personal Finance Tracker Dashboard!", font=("Arial", 16))
        welcome_label.pack(pady=(20, 10))

        # Export Data button
        export_button = ttk.Button(self, text="Export Data", style='Accent.TButton', command=self.export_data)
        export_button.place(relx=0.95, rely=0.15, anchor="ne")  # Butonu biraz aşağıya taşıdık

        # Form to add a new transaction
        self.create_transaction_form()

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        manage_categories_button = ttk.Button(
            button_frame, text="Manage Categories", style='Accent.TButton', command=self.manage_categories
        )
        manage_categories_button.grid(row=0, column=4, padx=10)

        # Style for buttons
        self.style = ttk.Style()
        self.style.configure('Accent.TButton', background='#5DADE2', foreground='white', font=('Arial', 12))
        self.style.map('Accent.TButton', background=[('active', '#3498DB')])

        # Add Transaction button
        add_transaction_button = ttk.Button(
            button_frame, text="Add Transaction", style='Accent.TButton', command=self.add_transaction
        )
        add_transaction_button.grid(row=0, column=0, padx=10)

        # Delete Transaction button
        delete_transaction_button = ttk.Button(
            button_frame, text="Delete Transaction", style='Accent.TButton', command=self.delete_transaction
        )
        delete_transaction_button.grid(row=0, column=1, padx=10)

        # View Transactions button
        view_transactions_button = ttk.Button(
            button_frame, text="View Transactions", style='Accent.TButton', command=self.view_transactions
        )
        view_transactions_button.grid(row=0, column=2, padx=10)

        # Filter Transactions button
        filter_button = ttk.Button(
            button_frame, text="Filter Transactions", style='Accent.TButton', command=self.open_filter_window
        )
        filter_button.grid(row=0, column=3, padx=10)

        # Logout button
        logout_button = ttk.Button(self, text="Logout", command=self.logout)
        logout_button.place(relx=0.95, rely=0.95, anchor="se")

        # Summary button
        summary_button = ttk.Button(self, text="Summary", command=self.show_summary)
        summary_button.place(relx=0.05, rely=0.95, anchor="sw")

        # Show Chart button
        chart_button = ttk.Button(self, text="Show Chart", command=self.show_chart)
        chart_button.place(relx=0.50, rely=0.95, anchor="s")

    def export_data(self):
        """Export user's transactions to CSV, Excel, or PDF."""
        # Ask user to choose the export format
        format_window = tk.Toplevel(self)
        format_window.title("Select Export Format")
        format_window.geometry("500x200")

        ttk.Label(format_window, text="Select the format to export:", font=("Arial", 12)).pack(pady=10)

        button_frame = ttk.Frame(format_window)
        button_frame.pack(pady=10)

        csv_button = ttk.Button(button_frame, text="CSV", command=lambda: self.save_file('csv', format_window))
        csv_button.grid(row=0, column=0, padx=10)

        excel_button = ttk.Button(button_frame, text="Excel", command=lambda: self.save_file('excel', format_window))
        excel_button.grid(row=0, column=1, padx=10)

        pdf_button = ttk.Button(button_frame, text="PDF", command=lambda: self.save_file('pdf', format_window))
        pdf_button.grid(row=0, column=2, padx=10)

    def save_file(self, file_format, format_window):
        """Handle the file saving based on selected format."""
        format_window.destroy()  # Close the format selection window

        if file_format == 'csv':
            filetypes = [('CSV files', '*.csv')]
            defaultextension = '.csv'
        elif file_format == 'excel':
            filetypes = [('Excel files', '*.xlsx')]
            defaultextension = '.xlsx'
        elif file_format == 'pdf':
            filetypes = [('PDF files', '*.pdf')]
            defaultextension = '.pdf'

        filename = filedialog.asksaveasfilename(
            defaultextension=defaultextension,
            filetypes=filetypes,
            title='Save Transactions As'
        )

        if filename:
            transactions = user_model.get_transactions(self.user_id)
            if not transactions:
                messagebox.showwarning("No Data", "No transactions to export.")
                return

            if file_format == 'csv':
                success = user_model.export_transactions_to_csv(self.user_id, filename)
                if success:
                    messagebox.showinfo("Success", f"Transactions exported successfully to {filename}")
                else:
                    messagebox.showerror("Error", "An error occurred during export.")
            elif file_format == 'excel':
                success = self.export_transactions_to_excel(transactions, filename)
                if success:
                    messagebox.showinfo("Success", f"Transactions exported successfully to {filename}")
                else:
                    messagebox.showerror("Error", "An error occurred during export.")
            elif file_format == 'pdf':
                success = self.export_transactions_to_pdf(transactions, filename)
                if success:
                    messagebox.showinfo("Success", f"Transactions exported successfully to {filename}")
                else:
                    messagebox.showerror("Error", "An error occurred during export.")

    def export_transactions_to_excel(self, transactions, filename):
        """Export transactions to an Excel file with text wrapping in the Description column."""
        try:
            # Convert transactions to a DataFrame
            df = pd.DataFrame(transactions, columns=['ID', 'User ID', 'Price', 'Category', 'Type', 'Date', 'Description'])

            # Create a Pandas Excel writer using XlsxWriter as the engine
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Transactions')

            # Get the xlsxwriter workbook and worksheet objects
            workbook  = writer.book
            worksheet = writer.sheets['Transactions']

            # Set the column width and format
            worksheet.set_column('A:G', 20)

            # Create a format for text wrapping
            wrap_format = workbook.add_format({'text_wrap': True})

            # Apply the text wrap format to the Description column
            worksheet.set_column('G:G', 30, wrap_format)

            # Close the Pandas Excel writer and output the Excel file
            writer.save()

            return True
        except Exception as e:
            print(f"An error occurred during Excel export: {e}")
            return False

    def export_transactions_to_pdf(self, transactions, filename):
        """Export transactions to a PDF file with wrapped text in the Description field."""
        try:
            c = pdf_canvas.Canvas(filename, pagesize=letter)
            width, height = letter

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Transactions Report")

            c.setFont("Helvetica", 12)
            text_y = height - 80

            # Define table headers
            headers = ['ID', 'Price', 'Category', 'Type', 'Date', 'Description']

            # Prepare data for the table
            data = [headers]

            for transaction in transactions:
                desc = transaction[6]
                # Wrap the description text
                wrapped_desc = simpleSplit(desc, 'Helvetica', 12, 200)
                data.append([
                    str(transaction[0]),  # ID
                    f"${transaction[2]:.2f}",  # Price
                    transaction[3],  # Category
                    transaction[4],  # Type
                    transaction[5],  # Date
                    '\n'.join(wrapped_desc)  # Wrapped Description
                ])

            # Create a table
            table = Table(data, colWidths=[50, 60, 80, 60, 80, 200])

            # Add style to the table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
            ])
            table.setStyle(style)

            # Calculate available space on the page
            available_height = text_y - 50

            # Build the table and split if necessary
            table.wrapOn(c, width, available_height)
            table_height = table._height

            if table_height < available_height:
                table.drawOn(c, 50, text_y - table_height)
            else:
                # If table is too long, split it
                from reportlab.platypus import SimpleDocTemplate
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = [table]
                doc.build(elements)
                c.save()
                return True

            c.save()
            return True
        except Exception as e:
            print(f"An error occurred during PDF export: {e}")
            return False

    def show_chart(self):
        """Display a detailed window with financial summaries and a Pie Chart that resizes and handles long category names."""
        # Get total income and expenses
        total_income, total_expenses = user_model.get_financial_summary(self.user_id)
        remaining_balance = total_income - total_expenses
    
        # Format amounts to two decimal places
        total_income_str = "${:.2f}".format(total_income)
        total_expenses_str = "${:.2f}".format(total_expenses)
        remaining_balance_str = "${:.2f}".format(remaining_balance)
    
        # Create a new window for the chart
        chart_window = tk.Toplevel(self)
        chart_window.geometry("900x850")
        #chart_window.resizable(False, False)
        chart_window.title("Financial Overview")
        chart_window.geometry("900x850")  # Daha geniş bir pencere boyutu
        chart_window.resizable(False, False)  # Allow window resizing
    
        # Create a frame for the header
        header_frame = ttk.Frame(chart_window)
        header_frame.pack(pady=10)
    
        # Window Title
        title_label = ttk.Label(header_frame, text="Financial Overview", font=("Arial", 18, "bold"))
        title_label.pack()
    
        # Create a frame for the summaries and button
        summary_frame = ttk.Frame(chart_window)
        summary_frame.pack(pady=10)
    
        # Display financial summaries
        summary_inner_frame = ttk.Frame(summary_frame)
        summary_inner_frame.pack()
    
        labels = ["Total Income:", "Total Expenses:", "Net Profit/Loss:"]
        amounts = [total_income_str, total_expenses_str, remaining_balance_str]
    
        for i, (label_text, amount_text) in enumerate(zip(labels, amounts)):
            label = ttk.Label(summary_inner_frame, text=label_text, font=("Arial", 12, "bold"))
            label.grid(row=i, column=0, sticky="w", padx=10, pady=2)
            amount_label = ttk.Label(summary_inner_frame, text=amount_text, font=("Arial", 12))
            amount_label.grid(row=i, column=1, sticky="e", padx=10, pady=2)
    
        # Chart Title
        chart_title_label = ttk.Label(chart_window, text="Expenses by Category", font=("Arial", 14))
        chart_title_label.pack(pady=5)
    
        # Create a frame for the legend
        legend_frame = ttk.Frame(chart_window)
        legend_frame.pack(pady=5)
    
        # Change Chart Button
        change_chart_button = ttk.Button(
            summary_frame,
            text="Change Chart",
            command=lambda: self.toggle_chart(canvas, ax, fig, chart_title_label, legend_frame)
        )
        change_chart_button.pack(pady=10)
    
        # Create the initial Pie Chart (Expenses by Category)
        fig, ax = plt.subplots(figsize=(8, 8))
        self.current_chart = 'category'  # Keep track of current chart type
    
        # Get expenses by category
        expenses_by_category = user_model.get_expenses_by_category(self.user_id)
    
        if not expenses_by_category:
            messagebox.showinfo("No Data", "No expense data available to display.")
            chart_window.destroy()
            return
    
        categories = list(expenses_by_category.keys())
        amounts = list(expenses_by_category.values())
    
        # Handle long category names by wrapping text
        wrapped_categories = ['\n'.join(textwrap.wrap(label, 15)) for label in categories]
    
        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=wrapped_categories,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10},
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
        )
        ax.axis('equal')
        ax.set_title('Expenses by Category')
    
        # Remove the default matplotlib legend
        # ax.legend(...)
    
        # Create a custom legend using Tkinter
        self.create_custom_legend(legend_frame, categories, ax.patches)
    
        # Apply tight layout
        fig.tight_layout()
    
        # Embed the chart in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=False)  # Allow canvas to expand
        canvas.get_tk_widget().config(width=600, height=400)
        # Update the chart when the window is resized
        def on_resize(event):
            # Prevent excessive redraws
            if event.widget == chart_window:
                new_width = event.width / 100
                new_height = event.height / 100
                fig.set_size_inches(new_width, new_height)
                fig.tight_layout()
                canvas.draw()
        chart_window.bind('<Configure>', lambda event: canvas.draw())  # Her boyutlandırmada yeniden çizim

    def toggle_chart(self, canvas, ax, fig, chart_title_label, legend_frame):
        """Toggle the Pie Chart between Income vs Expenses and Expenses by Category"""
        ax.clear()  # Clear the current axes

        if self.current_chart == 'category':
            # Switch to Income vs Expenses chart
            total_income, total_expenses = user_model.get_financial_summary(self.user_id)
            if total_income == 0 and total_expenses == 0:
                messagebox.showinfo("No Data", "No income or expense data available to display.")
                return
            amounts = [total_income, total_expenses]
            labels = ['Income', 'Expenses']
            colors = ['green', 'red']

            wedges, texts, autotexts = ax.pie(
                amounts,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'fontsize': 12},
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
            )
            ax.axis('equal')
            ax.set_title('Income vs Expenses')
            chart_title_label.config(text="Income vs Expenses")

            # Remove the old legend
            for widget in legend_frame.winfo_children():
                widget.destroy()

            # Create a new custom legend
            self.create_custom_legend(legend_frame, labels, wedges, colors)

            self.current_chart = 'income_expense'
        else:
            # Switch to Expenses by Category chart
            expenses_by_category = user_model.get_expenses_by_category(self.user_id)
            if not expenses_by_category:
                messagebox.showinfo("No Data", "No expense data available to display.")
                return
            categories = list(expenses_by_category.keys())
            amounts = list(expenses_by_category.values())

            # Handle long category names by wrapping text
            wrapped_categories = ['\n'.join(textwrap.wrap(label, 15)) for label in categories]

            wedges, texts, autotexts = ax.pie(
                amounts,
                labels=wrapped_categories,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10},
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
            )
            ax.axis('equal')
            ax.set_title('Expenses by Category')
            chart_title_label.config(text="Expenses by Category")

            # Remove the old legend
            for widget in legend_frame.winfo_children():
                widget.destroy()

            # Create a new custom legend
            self.create_custom_legend(legend_frame, categories, wedges)

            self.current_chart = 'category'

        # Apply tight layout and redraw the canvas
        fig.tight_layout()
        canvas.draw()


    def create_custom_legend(self, parent_frame, labels, patches, colors=None):
        """
        Create a custom legend using Tkinter widgets.
        :param parent_frame: The Tkinter frame where the legend will be placed.
        :param labels: List of label strings.
        :param patches: List of matplotlib Patch objects.
        :param colors: Optional list of colors if patches do not contain color information.
        """
        # Clear any existing widgets in the legend frame
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Create a title for the legend
        legend_title = ttk.Label(parent_frame, text="Categories", font=("Arial", 14, "bold"))
        legend_title.pack(anchor='w')

        # Create a frame for the legend entries
        entries_frame = ttk.Frame(parent_frame)
        entries_frame.pack(anchor='w', pady=5)

        for i, label in enumerate(labels):
            # Get the color from the patch or use the provided color list
            if colors:
                color = colors[i] if i < len(colors) else 'black'
            else:
                color = patches[i].get_facecolor()
                if isinstance(color, tuple) or isinstance(color, list):
                    # Convert RGBA to HEX
                    color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                else:
                    color = 'black'

            # Create a colored square
            color_label = ttk.Label(entries_frame, background=color, width=2)
            color_label.pack(side='left', padx=(0,5))

            # Create the text label
            text_label = ttk.Label(entries_frame, text=label, font=("Arial", 12))
            text_label.pack(side='left', padx=(0,15))

        # Add some padding at the bottom
        entries_frame.pack(pady=(0,10))
    

    def logout(self):
        self.master.show_login_window()

    def create_transaction_form(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)

        # Price (formerly Amount)
        price_frame = ttk.Frame(form_frame)
        price_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ttk.Label(form_frame, text="Price:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(price_frame, textvariable=self.price_var, font=("Arial", 12), width=18)
        self.price_entry.pack(side='left')
        ttk.Label(price_frame, text="$", font=("Arial", 12)).pack(side='left')

        # Validate that only numbers are entered
        def validate_price(action, value_if_allowed):
            if action == '1':  # Insertion
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
            else:
                return True  # Deletion is always allowed

        vcmd = (self.register(validate_price), '%d', '%P')
        self.price_entry.config(validate='key', validatecommand=vcmd)

        # Kategori Bölümü
        ttk.Label(form_frame, text="Category:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        categories = user_model.get_categories(self.user_id)
        if not categories:
            categories = ["General"]
        self.category_var = tk.StringVar(value=categories[0])
        self.category_menu = ttk.Combobox(
            form_frame, textvariable=self.category_var, values=categories, font=("Arial", 12), state='readonly', width=20
        )
        self.category_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Add Category button
        add_category_button = ttk.Button(
            form_frame, text="+", width=3, command=self.open_add_category_window
        )
        add_category_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")


        # Type
        ttk.Label(form_frame, text="Type:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.type_var = tk.StringVar(value="Expense")
        self.type_menu = ttk.Combobox(
            form_frame, textvariable=self.type_var, values=["Income", "Expense"], font=("Arial", 12), state='readonly'
        )
        self.type_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Date
        ttk.Label(form_frame, text="Date:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = ttk.Entry(form_frame, width=20, font=("Arial", 12))
        self.date_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Description
        ttk.Label(form_frame, text="Description:", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="ne")
        self.description_text = tk.Text(form_frame, width=40, height=4, font=("Arial", 12), wrap="word")
        self.description_text.grid(row=4, column=1, padx=10, pady=5, sticky="w")


    def manage_categories(self):
        """Kategori yönetimi penceresini açar."""
        manage_window = tk.Toplevel(self)
        manage_window.title("Manage Categories")
        manage_window.geometry("400x400")

        ttk.Label(manage_window, text="Your Categories", font=("Arial", 14)).pack(pady=10)

        categories = user_model.get_categories(self.user_id)

        list_frame = ttk.Frame(manage_window)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        category_listbox = tk.Listbox(list_frame, font=("Arial", 12), yscrollcommand=scrollbar.set)
        for category in categories:
            category_listbox.insert(tk.END, category)
        category_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=category_listbox.yview)

        # Kategori Silme Butonu
        ttk.Button(
            manage_window, text="Delete Selected Category",
            command=lambda: self.delete_category(category_listbox)
        ).pack(pady=10)

    def open_add_category_window(self):
        add_category_window = tk.Toplevel(self)
        add_category_window.title("Add Category")
        add_category_window.geometry("300x150")
        ttk.Label(add_category_window, text="Category Name:", font=("Arial", 12)).pack(pady=10)
        category_name_entry = ttk.Entry(add_category_window, font=("Arial", 12))
        category_name_entry.pack(pady=5)
        ttk.Button(
            add_category_window, text="Add",
            command=lambda: self.add_category(category_name_entry.get(), add_category_window)
        ).pack(pady=10)


    def add_category(self, category_name, window):
        if category_name:
            if user_model.add_category(self.user_id, category_name):
                self.update_category_menu()
                messagebox.showinfo("Success", "Category added successfully!")
                window.destroy()
            else:
                messagebox.showerror("Error", "Category already exists.")
        else:
            messagebox.showerror("Error", "Please enter a category name.")


    def delete_category(self, listbox):
        selected = listbox.curselection()
        if selected:
            category_name = listbox.get(selected[0])
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{category_name}'?")
            if confirm:
                if user_model.delete_category(self.user_id, category_name):
                    listbox.delete(selected[0])
                    self.update_category_menu()
                    messagebox.showinfo("Success", "Category deleted successfully!")
                else:
                    messagebox.showerror("Error", "An error occurred while deleting the category.")
        else:
            messagebox.showwarning("No Selection", "Please select a category to delete.")
        

    def update_category_menu(self):
        categories = user_model.get_categories(self.user_id)
        self.category_menu['values'] = categories


    def add_transaction(self):
        price = self.price_var.get()
        if not price:
            messagebox.showerror("Error", "Please enter the price.")
            return

        try:
            amount = float(price)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")
            return

        category = self.category_var.get()
        transaction_type = self.type_var.get().lower()
        date_input = self.date_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()

        if not date_input:
            messagebox.showerror("Error", "Please enter the date.")
            return

        parsed_date = dateparser.parse(date_input)
        if parsed_date:
            date = parsed_date.strftime("%Y-%m-%d")
        else:
            messagebox.showerror("Error", "Invalid date format. Please try again.")
            return

        # Add the transaction without tags
        transaction_id = user_model.add_transaction(self.user_id, amount, category, transaction_type, date, description)

        messagebox.showinfo("Success", "Transaction added successfully!")
        self.clear_form()


    def clear_form(self):
        self.price_var.set("")
        categories = user_model.get_categories(self.user_id)
        if categories:
            self.category_var.set(categories[0])
        else:
            self.category_var.set("General")
        self.type_var.set("Expense")
        self.date_entry.delete(0, "end")
        self.description_text.delete("1.0", "end")
        #self.tags_entry.delete(0, "end")

    def delete_transaction(self):
        transactions = user_model.get_transactions(self.user_id)

        if not transactions:
            messagebox.showinfo("No Transactions", "No transactions to delete.")
            return

        delete_window = tk.Toplevel(self)
        delete_window.title("Delete Transaction")
        delete_window.geometry("600x400")

        canvas = tk.Canvas(delete_window)
        scrollbar = ttk.Scrollbar(delete_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, transaction in enumerate(transactions):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(pady=5, padx=10, fill='x')

            ttk.Label(frame, text=f"Transaction {idx + 1}:", font=("Arial", 12)).grid(row=0, column=0, padx=5, sticky="w")
            ttk.Label(frame, text=f"Price: ${transaction[2]:.2f}", font=("Arial", 10)).grid(row=0, column=1, padx=5, sticky="w")
            ttk.Label(frame, text=f"Category: {transaction[3]}", font=("Arial", 10)).grid(row=0, column=2, padx=5, sticky="w")
            ttk.Label(frame, text=f"Type: {transaction[4]}", font=("Arial", 10)).grid(row=0, column=3, padx=5, sticky="w")
            ttk.Label(frame, text=f"Date: {transaction[5]}", font=("Arial", 10)).grid(row=0, column=4, padx=5, sticky="w")

            delete_button = ttk.Button(
                frame, text="Delete", command=lambda t_id=transaction[0]: self.confirm_delete(t_id, delete_window)
            )
            delete_button.grid(row=0, column=5, padx=5)

    def confirm_delete(self, transaction_id, delete_window):
        result = messagebox.askyesno("Delete Transaction", "Are you sure you want to delete this transaction?")
        if result:
            user_model.delete_transaction(transaction_id)
            messagebox.showinfo("Deleted", "Transaction deleted successfully.")
            delete_window.destroy()
            self.delete_transaction()  # Refresh the delete window

    def open_filter_window(self):
        filter_window = tk.Toplevel(self)
        filter_window.title("Filter Transactions")
        filter_window.geometry("400x300")

        ttk.Label(filter_window, text="Filter Transactions", font=("Arial", 14)).pack(pady=10)

        # Category Selection
        ttk.Label(filter_window, text="Category:", font=("Arial", 12)).pack(pady=5)
        category_var = tk.StringVar()
        categories = ["All"] + user_model.get_categories(self.user_id)
        category_menu = ttk.Combobox(filter_window, textvariable=category_var, values=categories, font=("Arial", 12), state='readonly')
        category_menu.current(0)
        category_menu.pack(pady=5)

        # Tags Entry
        ttk.Label(filter_window, text="Tags (comma-separated):", font=("Arial", 12)).pack(pady=5)
        tags_entry = ttk.Entry(filter_window, width=40, font=("Arial", 12))
        tags_entry.pack(pady=5)

        # Filter Button
        ttk.Button(filter_window, text="Apply Filter", command=lambda: self.apply_filter(category_var.get(), tags_entry.get(), filter_window)).pack(pady=10)

    def apply_filter(self, category, tags_input, window):
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        if category == "All":
            category = None
        transactions = user_model.get_transactions_filtered(self.user_id, category, tags)
        window.destroy()
        self.view_transactions(transactions)

    def view_transactions(self, transactions=None):
        if transactions is None:
            transactions = user_model.get_transactions(self.user_id)

        view_window = tk.Toplevel(self)
        view_window.title("View Transactions")
        view_window.geometry("600x400")

        canvas = tk.Canvas(view_window)
        scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, transaction in enumerate(transactions):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(pady=5, padx=10, fill='x')

            ttk.Label(frame, text=f"Transaction {idx+1}:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
            ttk.Label(frame, text=f"Price: ${transaction[2]:.2f}", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
            ttk.Label(frame, text=f"Category: {transaction[3]}", font=("Arial", 10)).grid(row=1, column=1, sticky="w")
            ttk.Label(frame, text=f"Type: {transaction[4]}", font=("Arial", 10)).grid(row=1, column=2, sticky="w")
            ttk.Label(frame, text=f"Date: {transaction[5]}", font=("Arial", 10)).grid(row=1, column=3, sticky="w")
            ttk.Label(frame, text=f"Description: {transaction[6]}", font=("Arial", 10)).grid(row=2, column=0, columnspan=4, sticky="w")
            # Display tags
            tags = user_model.get_tags_for_transaction(transaction[0])
            if tags:
                ttk.Label(frame, text=f"Tags: {', '.join(tags)}", font=("Arial", 10)).grid(row=3, column=0, columnspan=4, sticky="w")
            ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=5)

    def show_summary(self):
        total_income, total_expenses = user_model.get_financial_summary(self.user_id)
        remaining_balance = total_income - total_expenses

        summary_window = tk.Toplevel(self)
        summary_window.title("Financial Summary")
        summary_window.geometry("400x200")

        total_income_str = "${:.2f}".format(total_income)
        total_expenses_str = "${:.2f}".format(total_expenses)
        remaining_balance_str = "${:.2f}".format(remaining_balance)

        labels = ["Total Income:", "Total Expenses:", "Remaining Balance:"]
        amounts = [total_income_str, total_expenses_str, remaining_balance_str]

        for i, (label_text, amount_text) in enumerate(zip(labels, amounts)):
            label = ttk.Label(summary_window, text=label_text, font=("Arial", 14, "bold"))
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            amount_label = ttk.Label(summary_window, text=amount_text, font=("Arial", 14))
            amount_label.grid(row=i, column=1, sticky="e", padx=10, pady=5)

if __name__ == "__main__":
    app = FinanceTrackerApp()
    app.mainloop()
