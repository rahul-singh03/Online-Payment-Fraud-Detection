# Online Payment Fraud Detection Using Machine Learning

### Real-time Analysis with OCR, Flask & Geolocation

This project was developed as part of our final year B.Tech (CSE) program at Durgapur Institute of Advanced Technology and Management, 
aiming to address the growing threat of fraud in UPI and digital payments. 
Our goal was to build a practical system that uses machine learning and OCR to detect fraudulent transactions in real time.

## What This System Does

- Accepts uploaded UPI payment screenshots
- Extracts key info using **Tesseract OCR**
- Applies a trained **ML model (Random Forest)** to predict fraud
- Stores results along with **timestamp and geolocation**
- Provides consistent output for repeated uploads (via image hashing)

## Tech Stack

- **Backend:** Python, Flask
- **OCR:** Tesseract
- **ML Models:** Random Forest
- **Libraries:** OpenCV, Pandas, NumPy, Scikit-learn
- **Frontend:** HTML/CSS, JavaScript
- **Map Integration:** Google Maps API

---

## Dataset Used

- Sourced from Kaggle: [Online Payments Fraud Detection Dataset](https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset)

---

## Machine Learning Overview

- **Features Extracted:** Amount, UPI ID, Date/Time, Transaction ID
- **Additional Features:** User behavior, location info
- **SMOTE** used for class imbalance handling
- **Random Forest** gave best results (~72% accuracy)
- Implemented **hash-based logic** for duplicate fraud detection

---

## Features Implemented

- Screenshot upload & OCR-based data extraction
- Real-time prediction of fraud
- Upload history tracking with location data
- Consistent fraud score for same screenshot
- Frontend validations (age-restricted signup, form checks)
- Google Maps view for uploaded transactions

---

## Research Publications

We published two research papers at different stages of this project:

1. **"Enhancing Online Payment Security using ML: Advanced Techniques for Fraud Detection in Digital Transactions"**  
   *(JETIR, Vol. 11, Issue 12, Dec 2024)*  
   🔗 [JETIR Paper](https://www.jetir.org/view?paper=JETIR2412319)  
   > Focused on theoretical methods and proposed design using Random Forest, Gradient Boosting, and extensive feature engineering. Published during the idea phase.

2. **"Online Payment Fraud Detection using Machine Learning: An Implementation using Flask, OCR and Real-time Transaction Analysis"**  
   *(IJNRD, Vol. 10, Issue 4, Apr 2025)*  
   🔗 [IJNRD Paper](https://ijnrd.org/viewpaperforall.php?paper=IJNRD2504501)  
   > Describes the implemented version of the system with Flask, OCR integration, and real-time fraud detection logic.

> **Note:** The two papers reflect different project stages — the first conceptual, the second post-implementation. Not all proposed features could be integrated due to time and resource constraints, but the core objective was achieved.

---
