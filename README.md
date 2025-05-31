# PulseTrend.ai
Mind Spark Hackfest 2025

# Sales Prediction and Dashboard

This project provides a Flask-based backend server that forecasts product sales, generates keyword trends, and supports various analytics features. It leverages Prophet for time-series forecasting and Google Charts for frontend visualization.

---

## 🚀 Features

✅ Product sales forecasting (using Prophet)  
✅ Keyword trend analysis  
✅ JSON APIs for dashboard integration  
✅ Integration with preprocessed product and sales data  

---

## 📦 Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)
- **nltk** (for text preprocessing)
- **prophet** (for time-series forecasting)

---

## 🔧 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
````

2. **Set up the Python environment**
   It’s recommended to use a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use venv\\Scripts\\activate
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run NLTK Setup Script**
   (Download necessary NLTK resources)

   ```bash
   python install.nltk.py
   ```

---

## ⚙️ Usage

1. **Start the Flask Server**

   ```bash
   python server.py
   ```

2. **Access the Dashboard**

   Open your browser and navigate to:

   ```
   http://localhost:5000
   ```

---

## 🗂️ Data Files

* **sales-data.csv**: Contains sales records by product ID and date.
* **product\_catalog.csv**: Contains product metadata (title, description, category).

Ensure these files are placed in the appropriate folder (`./content/` by default).

---

## 💡 Notes

* Customize the server routes as needed for additional endpoints.
* Prophet may take a few seconds to train, especially with larger datasets.

---

## 🤝 Contributions

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

* Prophet: [https://facebook.github.io/prophet/](https://facebook.github.io/prophet/)
* Google Charts: [https://developers.google.com/chart](https://developers.google.com/chart)

---

```

---

### 🔧 Notes:
✅ You might want to add a `requirements.txt` with dependencies like `Flask`, `pandas`, `prophet`, and `nltk` if not already done.  
✅ Adjust the **GitHub repository URL** under **Clone the Repository** if you’d like to host it online.  
✅ Let me know if you’d like to integrate deployment instructions (e.g. Heroku, Docker) or add sample API usage examples! 🚀📊
```
