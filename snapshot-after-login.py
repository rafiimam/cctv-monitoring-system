import base64
import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def login_and_take_screenshot(url, username, password):
    # Set up Selenium with Chrome
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode
    
    # Use webdriver_manager to automatically get the correct ChromeDriver
    service = ChromeService(ChromeDriverManager().install())  # Create a Service object

    # Pass the service object to the webdriver.Chrome constructor
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open the login page
        driver.get(url)

        # Locate the username and password fields and the login button
        username_field = driver.find_element(By.ID, "email")  # Change this as needed
        password_field = driver.find_element(By.NAME, "pass")  # Change this as needed
        login_button = driver.find_element(By.NAME, "login")  # Change this as needed

        # Input credentials
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()  # Click the login button

        # Wait for a bit to ensure login completes
        time.sleep(5)  # Adjust this if necessary

        # Take a screenshot after logging in
        screenshot = driver.get_screenshot_as_png()  # Take screenshot
    finally:
        driver.quit()  # Clean up the driver

    return screenshot

def save_to_mongodb(screenshot, url):
    # Convert screenshot to Base64
    screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["screenshots"]  # Database name
    collection = db["screenshots"]  # Collection name

    # Create a document
    document = {
        "url": url,
        "screenshot": screenshot_b64
    }

    # Insert the document into the collection
    collection.insert_one(document)

    print(f"Screenshot for {url} saved to MongoDB.")
    messagebox.showinfo("Success", f"Screenshot for {url} saved to MongoDB.")

def on_submit():
    url = url_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    
    if not url or not username or not password:
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    # Check if the URL is valid
    if not url.startswith("http://") and not url.startswith("https://"):
        messagebox.showwarning("Invalid URL", "Please enter a valid URL (e.g., http://example.com).")
        return

    try:
        screenshot = login_and_take_screenshot(url, username, password)
        save_to_mongodb(screenshot, url)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = tk.Tk()
root.title("Screenshot with Login")

# Create and place the labels and entries
tk.Label(root, text="URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=10)
username_entry = tk.Entry(root, width=50)
username_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=10)
password_entry = tk.Entry(root, show="*", width=50)
password_entry.grid(row=2, column=1, padx=10, pady=10)

# Create and place the submit button
submit_button = tk.Button(root, text="Take Screenshot", command=on_submit)
submit_button.grid(row=3, column=0, columnspan=2, pady=10)

# Start the GUI event loop
root.mainloop()
