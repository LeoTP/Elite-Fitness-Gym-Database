from tkinter import *
from tkinter import messagebox
from gym_backend import create_db, add_member, clear_database, get_all_members, connect_db

# create_db()
# 
# def refresh_table():
#     # Clear current rows
#     for row in tree.get_children():
#         tree.delete(row)
# 
#     # Insert fresh rows
#     for member in get_all_members():
#         tree.insert("", END, values=member)
# 
# def add_member_ui():
#     try:
#         name = name_entry.get()
#         email = email_entry.get()
#         age = int(age_entry.get())
#         height = float(height_entry.get())
#         weight = float(weight_entry.get())
#         next_payment = next_payment_entry.get()
# 
#         add_member(name, email, age, height, weight, next_payment)
#         messagebox.showinfo("Success", "Member added!")
#         refresh_table()
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         
# 
# # --- UI Layout ---
# root = Tk()
# root.title("Elite Fitness Gym")
# 
# Label(root, text="Name").grid(row=0, column=0)
# name_entry = Entry(root); name_entry.grid(row=1, column=0)
# 
# Label(root, text="Email").grid(row=0, column=1)
# email_entry = Entry(root); email_entry.grid(row=1, column=1)
# 
# Label(root, text="Age").grid(row=0, column=2)
# age_entry = Entry(root); age_entry.grid(row=1, column=2)
# 
# Label(root, text="Height (m)").grid(row=0, column=3)
# height_entry = Entry(root); height_entry.grid(row=1, column=3)
# 
# Label(root, text="Weight (kg)").grid(row=0, column=4)
# weight_entry = Entry(root); weight_entry.grid(row=1, column=4)
# 
# Label(root, text="Next Payment (YYYY-MM-DD)").grid(row=0, column=5)
# next_payment_entry = Entry(root); next_payment_entry.grid(row=1, column=6)
# 
# Button(root, text="Add Member", command=add_member_ui).grid(row=6, column=0)
# #Button(root, text="View Members", command=view_members_ui).grid(row=6, column=1)
# #Button(root, text="Check Dues", command=check_due_ui).grid(row=7, column=0)
# #Button(root, text="Clear All", command=clear_all_ui).grid(row=7, column=1)
# 
# display_text = Text(root, height=15, width=60)
# display_text.grid(row=8, column=0, columnspan=2, pady=10)
# 
# root.mainloop()
# 
# #def main():
#     
#         
# #if __name__ == "__main__":
#    # main()

class EditableTable(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gym Members Manager - Editable Table")
        self.geometry("900x400")
        self.tree = None
        self.editing_entry = None
        self.current_edit = None  # (item, column)

        self.columns = ['ID', 'Name', 'Email', 'Age', 'Height', 'Weight', 'Next Payment']
        self.setup_widgets()
        self.load_data()
            
    def setup_widgets(self):
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind double-click to start editing
        self.tree.bind("<Double-1>", self.start_edit)
        
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = get_all_members()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

        # Add an empty row for new member entry
        self.tree.insert("", tk.END, values=("", "", "", "", "", "", ""))
        
    def start_edit(self, event):
        # Identify which row and column was clicked
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        rowid = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not rowid or not column:
            return

        x, y, width, height = self.tree.bbox(rowid, column)
        value = self.tree.set(rowid, column)

        # Convert Treeview column string e.g. "#1" to index
        col_index = int(column.replace('#', '')) - 1

        # Don't allow editing the ID column
        if col_index == 0:
            return

        # Create Entry widget overlay on top of the cell
        if self.editing_entry:
            self.editing_entry.destroy()

        self.editing_entry = tk.Entry(self.tree)
        self.editing_entry.place(x=x, y=y, width=width, height=height)
        self.editing_entry.insert(0, value)
        self.editing_entry.focus_set()

        # Store current editing cell info
        self.current_edit = (rowid, col_index)

        # Bind events for finishing editing
        self.editing_entry.bind("<Return>", self.finish_edit)
        self.editing_entry.bind("<FocusOut>", self.finish_edit)

    def finish_edit(self, event):
        if not self.editing_entry or not self.current_edit:
            return

        new_value = self.editing_entry.get()
        rowid, col_index = self.current_edit
        self.editing_entry.destroy()
        self.editing_entry = None

        old_values = list(self.tree.item(rowid, "values"))

        if rowid == self.tree.get_children()[-1]:  # last row = new member
            # If any required field is empty, ignore
            if col_index == 0:
                # ID col, ignore
                return
            # Insert new member if at least name or email is given (simple check)
            # Update the value user edited in the new member row
            old_values[col_index] = new_value
            # Check if any value present
            if any(old_values[1:]):
                try:
                    # Convert types where needed
                    age = int(old_values[3]) if old_values[3] else None
                    height = float(old_values[4]) if old_values[4] else None
                    weight = float(old_values[5]) if old_values[5] else None

                    new_member_data = (
                        old_values[1],    # name
                        old_values[2],    # email
                        age,
                        height,
                        weight,
                        old_values[6]     # next_payment
                    )
                    add_member(new_member_data)
                    messagebox.showinfo("Success", "New member added!")

                    # Reload table to show new member with ID
                    self.load_data()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add member:\n{e}")
            return

        # Editing existing member
        member_id = old_values[0]
        old_values[col_index] = new_value
        success = update_member(member_id, col_index, new_value)
        if success:
            self.tree.set(rowid, column=f"#{col_index+1}", value=new_value)
        else:
            messagebox.showerror("Error", "Failed to update member")

        self.current_edit = None


if __name__ == "__main__":
    create_db()
    app = EditableTable()
    app.mainloop()