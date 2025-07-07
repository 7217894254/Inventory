import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

# --- DATABASE SETUP ---
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
)
""")

conn.commit()

# --- GLOBALS ---
entry_name = entry_quantity = entry_price = listbox = None
root = tk.Tk()

# --- AUTH FUNCTIONS ---
def register_user():
    username = simpledialog.askstring("Register", "Enter Username:")
    password = simpledialog.askstring("Register", "Enter Password:", show="*")
    if not username or not password:
        messagebox.showerror("Error", "Username and password cannot be empty")
        return
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

def login_user():
    username = simpledialog.askstring("Login", "Enter Username:")
    password = simpledialog.askstring("Login", "Enter Password:", show="*")
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if cursor.fetchone():
        messagebox.showinfo("Success", "Login Successful")
        open_inventory_window()
    else:
        messagebox.showerror("Error", "Invalid credentials")

# --- INVENTORY FUNCTIONS ---
def add_product():
    name = entry_name.get().strip()
    try:
        quantity = int(entry_quantity.get())
        price = float(entry_price.get())
    except:
        messagebox.showerror("Error", "Invalid quantity or price")
        return

    if name == "":
        messagebox.showerror("Error", "Product name cannot be empty")
        return

    try:
        cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
        conn.commit()
        update_inventory_list()
        clear_fields()
        messagebox.showinfo("Success", f"{name} added")
    except Exception as e:
        messagebox.showerror("Error", f"Could not add product: {e}")

def update_inventory_list():
    try:
        listbox.delete(0, tk.END)
        cursor.execute("SELECT id, name, quantity, price FROM products")
        rows = cursor.fetchall()

        if not rows:
            listbox.insert(tk.END, "No products found.")
            return

        for row in rows:
            pid, pname, qty, prc = row
            listbox.insert(tk.END, f"{pid} - {pname} | Qty: {qty} | ₹{prc}")
            if qty < 5:
                listbox.insert(tk.END, "⚠️ Low Stock Alert!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load inventory: {e}")

def delete_product():
    try:
        selected = listbox.get(listbox.curselection())
        product_id = int(selected.split()[0])
        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        update_inventory_list()
    except:
        messagebox.showerror("Error", "Select a valid product to delete")

def edit_product():
    try:
        selected = listbox.get(listbox.curselection())
        product_id = int(selected.split()[0])
    except:
        messagebox.showerror("Error", "Select a valid product to edit")
        return

    new_qty = simpledialog.askinteger("Edit", "Enter new quantity:")
    new_price = simpledialog.askfloat("Edit", "Enter new price:")
    if new_qty is not None and new_price is not None:
        try:
            cursor.execute("UPDATE products SET quantity=?, price=? WHERE id=?", (new_qty, new_price, product_id))
            conn.commit()
            update_inventory_list()
        except:
            messagebox.showerror("Error", "Failed to update product")

def clear_fields():
    entry_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_price.delete(0, tk.END)

# --- INVENTORY WINDOW ---
def open_inventory_window():
    global entry_name, entry_quantity, entry_price, listbox
    root.withdraw()
    win = tk.Toplevel()
    win.title("Inventory Management System")
    win.geometry("500x400")

    tk.Label(win, text="Product Name:").grid(row=0, column=0)
    entry_name = tk.Entry(win)
    entry_name.grid(row=0, column=1)

    tk.Label(win, text="Quantity:").grid(row=1, column=0)
    entry_quantity = tk.Entry(win)
    entry_quantity.grid(row=1, column=1)

    tk.Label(win, text="Price:").grid(row=2, column=0)
    entry_price = tk.Entry(win)
    entry_price.grid(row=2, column=1)

    tk.Button(win, text="Add", command=add_product).grid(row=3, column=0)
    tk.Button(win, text="Edit", command=edit_product).grid(row=3, column=1)
    tk.Button(win, text="Delete", command=delete_product).grid(row=3, column=2)

    listbox = tk.Listbox(win, width=70)
    listbox.grid(row=4, column=0, columnspan=3, pady=10)

    update_inventory_list()

# --- LOGIN WINDOW ---
root.title("Login/Register")
root.geometry("300x150")

tk.Button(root, text="Register", command=register_user, width=25).pack(pady=10)
tk.Button(root, text="Login", command=login_user, width=25).pack(pady=10)

root.mainloop()


