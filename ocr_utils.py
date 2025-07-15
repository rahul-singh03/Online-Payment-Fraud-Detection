import pytesseract
import cv2
from PIL import Image
import re
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:/Users/RAHUL KUMAR SINGH/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

def preprocess_image(image_path):
    """Read and preprocess the image to improve OCR accuracy"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # optional: improve contrast or apply thresholding
    return gray

def extract_text(image_path):
    img = preprocess_image(image_path)
    text = pytesseract.image_to_string(img)
    return text



def parse_transaction_details(text):
    lines = text.lower().split('\n')
    data = {
        'transaction_status': None,
        'amount': None,
        'receiver_name': None,
        'upi_id': None,
        'date_time': None,
        'transaction_id': None,
        'utr': None,
        'bank_account': None
    }

    # 1. Transaction Status (robust detection)
    status_text = text.lower()

    if any(kw in status_text for kw in ['transaction failed', 'payment failed', 'failed']):
        data['transaction_status'] = 'failed'
    elif any(kw in status_text for kw in ['transaction successful', 'payment successful', 'paid successfully', 'success']):
        data['transaction_status'] = 'success'


    # 2. Amount
    amt_match = re.search(r'[%₹]\s?[\d,]+', text)  # accept ₹ or %
    if amt_match:
        data['amount'] = amt_match.group().replace('₹', '').replace(',', '').replace('%', '').strip()

    # 3. UPI ID
    upi_match = re.search(r'\b[\w\.\-]+@[\w]+\b', text)
    if upi_match:
        data['upi_id'] = upi_match.group()

    # 4. Receiver Name (try to extract name just before the UPI ID)
    name_match = re.search(r'payment to\s+([a-z\s\.]+)', text.lower())
    if name_match:
        data['receiver_name'] = name_match.group(1).title()
    else:
        # 4. Receiver Name (handle "Paid to" format and clean OCR noise)
        upi_lines = [line for line in lines if '@' in line]
        if upi_lines:
            upi_index = lines.index(upi_lines[0])
            if upi_index > 0:
                potential_name = re.sub(r'\d+', '', lines[upi_index - 1].strip())
                # Clean out numbers, special symbols, and ₹
                cleaned_name = re.sub(r'[^a-zA-Z\s\.]', '', potential_name).strip()
                # Only assign if it's within reasonable length
                if 3 <= len(cleaned_name) <= 40:
                    data['receiver_name'] = cleaned_name.title()



    # 5. Transaction ID
    txn_match = re.search(r't[0-9]{20,}', text.lower())  # usually starts with 'T' and 20+ digits
    if txn_match:
        data['transaction_id'] = txn_match.group()

    # 6. UTR
    utr_match = re.search(r'utr[:\s]+([0-9]+)', text.lower())
    if utr_match:
        data['utr'] = utr_match.group(1)

    # 7. Bank Account
    bank_match = re.search(r'xxxxxx\d{4}', text.lower())
    if bank_match:
        data['bank_account'] = bank_match.group().upper()

    # 8. Date and Time from text
    date_match = re.search(r'(\d{1,2}:\d{2}\s?(am|pm)).*?(\d{1,2}\s\w+\s20\d{2})', text.lower())
    if date_match:
        time_str = date_match.group(1)
        date_str = date_match.group(3)
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %I:%M %p")
            data['date_time'] = dt.strftime("%d %B %Y, %I:%M %p")
        except:
            pass

    return data



def get_upi_data_from_image(image_path):
    text = extract_text(image_path)
    return parse_transaction_details(text)
