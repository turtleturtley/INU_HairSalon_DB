# The Cut : INU (Hair Salon Price Comparison App)

**2025 Fall Semester Database Final Project**
**Student ID: 202302923 | Name: 박민정**

### 1. Project Overview
**The Cut : INU** is a web application designed to help students at Incheon National University compare hair salon prices around the campus. It collects scattered price information (cuts, perms, etc.) and organizes it into a database, allowing users to easily search, sort, and compare services.

### 2. Tech Stack
* **Language & Framework:** Python 3.x, Flask
* **Database:** SQLite3
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)

### 3. Database Structure (ERD)
* **Salons:** Stores salon information including name, location, and phone number.
* **Menus:** Stores service names and prices. (Has a **1:N relationship** with the `Salons` table).
* **Favorites:** Stores user-selected favorite salons.

### 4. Key Features
* **Search & Sort:** Users can search for salons by name or service and sort results by price (Low to High / High to Low).
* **Add Salon (Data Management):** Users can register new salons and menus directly. This process uses SQL transactions to update both `Salons` and `Menus` tables.
* **Favorites:** Users can 'like' salons to save them. This feature utilizes the `Favorites` table in the database to persist user choices.

### 5. How to Run
**Step 1. Initialize Database**
Run this command to create the database file (`database.db`) and insert initial data.
```bash
python init_db.py
```

**Step 2. Run Server**
Start the Flask application.
```bash
python app.py
```
After starting the server, open your browser and visit: `http://127.0.0.1:5001`

### 6. Data Source
* The initial data for 27 salons was manually collected and verified using **Naver Maps** based on the actual locations near Incheon National University.