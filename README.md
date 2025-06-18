# Brazil E-Commerce Dashboard ✨

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **Bangkit 2024 & DBS Coding Camp | Analysis Data with Python Submission**

An interactive dashboard for analyzing Brazilian e-commerce data using Python and Streamlit. This project provides comprehensive insights into sales patterns, customer behavior, product performance, and geographical distribution of orders across Brazil.

## 🎯 Project Overview

This dashboard analyzes the Brazilian E-Commerce Public Dataset from Kaggle, offering interactive visualizations and insights for:

- **Sales Performance Analysis**: Revenue trends, monthly/yearly patterns
- **Customer Behavior**: Order patterns, customer segmentation, retention analysis  
- **Product Analytics**: Best-selling products, category performance, review analysis
- **Geographical Insights**: Regional sales distribution, delivery performance by state
- **Operational Metrics**: Order status, delivery times, payment methods

## 📊 Features

- 📈 **Interactive Charts**: Dynamic visualizations using Plotly and Streamlit
- 🗺️ **Geospatial Analysis**: Brazil map visualization with sales distribution
- 📅 **Time Series Analysis**: Trend analysis with date range filtering
- 🎯 **Customer Segmentation**: RFM analysis and customer insights
- 📱 **Responsive Design**: Mobile-friendly dashboard interface
- 🔍 **Advanced Filtering**: Multi-dimensional data filtering capabilities

## 🛠️ Technologies Used

- **Python 3.8+**
- **Streamlit** - Web app framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive visualizations
- **NumPy** - Numerical computing
- **Matplotlib & Seaborn** - Statistical data visualization

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.8 or higher installed on your system.

### Installation

#### Option 1: Visual Studio Code (Windows)

```bash
# Create virtual environment
python -m venv submission

# Activate virtual environment
submission\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Shell/Terminal (Linux/Mac)

```bash
# Create project directory
mkdir submission
cd submission

# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Linux/Mac:
source venv/bin/activate
# For Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Run the Streamlit dashboard
streamlit run dashboard/dashboard.py
```

The dashboard will be available at `http://localhost:8501`

## 📁 Project Structure

```
ecommerce-analysis/
├── dashboard/
│   ├── dashboard.py          # Main Streamlit application
│   └── utils.py             # Helper functions (if applicable)
├── data/
│   └── *.csv                # Dataset files
├── notebooks/
│   └── analysis.ipynb       # Exploratory data analysis
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
└── LICENSE                 # License file
```

## 📈 Dashboard Sections

1. **Overview**: Key metrics and summary statistics
2. **Sales Analysis**: Revenue trends and performance metrics
3. **Customer Analytics**: Customer behavior and segmentation
4. **Product Performance**: Best-sellers and category analysis
5. **Geographic Distribution**: Regional sales patterns
6. **Operational Insights**: Delivery and logistics metrics

## 🎓 Learning Outcomes

This project demonstrates:

- **Data Analysis Skills**: Pandas for data manipulation and cleaning
- **Visualization Expertise**: Creating interactive dashboards with Streamlit
- **Statistical Analysis**: Customer segmentation and business metrics
- **Geographic Analysis**: Spatial data visualization techniques
- **Web Development**: Building and deploying data applications

## 📊 Dataset

The project uses the Brazilian E-Commerce Public Dataset by Olist, which contains:
- 100k+ orders from 2016 to 2018
- Order details, customer information, and product data
- Geolocation data for customers and sellers
- Product reviews and ratings

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 👨‍💻 Author

**LukasKrisna**
- GitHub: [@LukasKrisna](https://github.com/LukasKrisna)

## 🙏 Acknowledgments

- [Bangkit Academy](https://bangkit.academy/) for the learning opportunity
- [DBS Foundation](https://www.dbs.com/dbsfoundation) for the coding camp program
- [Olist](https://olist.com/) for providing the public dataset
- [Streamlit](https://streamlit.io/) for the amazing framework

---
