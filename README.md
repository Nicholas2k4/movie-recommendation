-----

## 🛠️ Tech Stack

  - **Backend**: Flask, Python
  - **ML & Vector Search**: LangChain, HuggingFace Transformers (`sentence-transformers`), Qdrant Client
  - **Frontend**: HTML, Bootstrap 5, jQuery, Select2.js
  - **Data Processing**: Pandas
  - **Dataset**: [The Movies Dataset @ Kaggle](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset/data)

-----

## 🚀 Getting Started

Follow these steps to run the application locally.

### 1\. Prerequisites

  - Python 3.9+
  - Git

### 2\. Clone the Repository

```bash
git clone https://github.com/Nicholas2k4/movie-recommendation.git
cd movie-recommendation
```

### 3\. Install Dependencies

It's recommended to use a virtual environment.

```bash
# Optional: Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install required packages
pip install -r requirements.txt
```

### 4\. Run the Web Application

Once the database is ready, start the Flask server:

```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.
