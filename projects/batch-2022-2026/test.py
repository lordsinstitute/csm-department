import tkinter as tk
from tkinter import messagebox

def show_message():
    messagebox.showinfo("Message", "Hello, this is a message!")

root = tk.Tk()
root.title("Button and Message Box Example")

# Frame for message box
message_frame = tk.Frame(root)
message_frame.pack(side="top", fill="both", expand=True)

# Message box
message_label = tk.Label(message_frame, text="Message Box")
message_label.pack(pady=10)

# Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(side="bottom", fill="x")

# Buttons
button1 = tk.Button(button_frame, text="Show Message", command=show_message)
button1.pack(side="left", padx=10, pady=10)

button2 = tk.Button(button_frame, text="Quit", command=root.quit)
button2.pack(side="right", padx=10, pady=10)

root.mainloop()
