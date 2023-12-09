# Could be made nicer for future work
import tkinter as tk
import json

def getResponse(jsonSTR: str):
    def yes_clicked():
        global response
        response = True
        root.destroy()

    def no_clicked():
        global response
        response = False
        root.destroy()

    root = tk.Tk()
    
    # Create a label to display the formatted JSON data
    label = tk.Label(root, text=jsonSTR, justify=tk.LEFT)
    label.pack(fill="both", expand=True, padx=10, pady=10)

    # Create a button to close the window
    button = tk.Button(root, text="Close", command=root.destroy)
    button.pack()

    label = tk.Label(root, text="Is the displayed action necessary?")
    label.pack()

    yes_button = tk.Button(root, text="Yes", command=yes_clicked)
    yes_button.pack()

    no_button = tk.Button(root, text="No", command=no_clicked)
    no_button.pack()
    print("lets see")
    root.mainloop()

    return response