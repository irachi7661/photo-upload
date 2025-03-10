from flask import Flask, render_template, request, send_from_directory, jsonify
import dropbox
import os
import random
import string
import json
import requests
import time
import threading

app = Flask(__name__)

# লোকাল আপলোড ফোল্ডার সেটআপ
UPLOAD_FOLDER = 'upload'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ড্রপবক্স ক্লায়েন্ট সেটআপ
dbx = dropbox.Dropbox('sl.u.AFkZwDPVWicN65YfgYCydBqublbJI8qLheA67a5z69-cCDseQ55NII7wvC7kkNetFiPh4p_jLVl1tWx5NDSiWzqzNzyOC5av4hVF1batOBUwkha3bZEeCRhG2uflWwOGGE26-Q0a7adezHIcOo3HXmZCumVQ1KgT_9EnPSMcp-UTVQBgJtfKpiZ-0wEBTQnV_f4HgPuQ8uNI4UsYJabHsr12iTr2szciyfPUfqt6xpGkJCTa3QwwMqWBow4JLQkueJ0gpncM_cyFbnVdBGHV20FUGn2IurADGXjSexj8NNipUvCls6YlePPbzkM0g4b-eJc0cmdjiBS-Ybrz74JXZp4pejvcB2FpYMtN_PoJI1Iz-549dDvEN9eC7XYoPx1SKWYNm9-avvxP0NjFHc5vFvIV0RMnnIcpWPTUmPca-okpV291nAu7NIUyYjjTE0BfMkepSh6CJCtLjm4EXj2qiJkhhh3Z8TemiGJMoaOVSYvcyfz-EUOyDkJD9ytZ7ba_rM2BdgG7ffrMTOemc_CK4TuWKutX3M36XL8TZNEZwtKcDUEmw3B0Ffo9j82Vr6UHZSiyI2BI1yf212AmoBSKsp50oR0RwPYP0gb7woYl803Iu7vNpJHAJ3Czr8sINwnF_qIFRNyUM09qkZzGq6y9lbKBo6AF4ZBNxNoo5izBxglGZwar9gTphNmX1Vym74Dv3UUi4BC6nEwSkqTUx5OTAOQ1FJukLbr75HSMEhjOfWCepL_0MwgNAi1Lj7z6O-EGArKaF-sMquV6aHtgKh4HozaLu-Zni2cBlCWSEtJPvsdaYJqPq8a0oMfrEnvhDcHnQwGrxYaaAsvSUI8LpFh_7MF2k1Te0ai616zZfZfmPZ5pD5QCxXqalLk36eUNaV2KFjBu7mRWG0WJlEZeeJeqgTWCcoXlw-VSs6790yDiNwS9beUVTPBPT5WPgqxTCFs8rc5NrQa5os9MH1FaTAACjRDVJtYYWwcIQSi7pIx5zQIddjwOyXwvvekF-KrVGfZC7Lkld4HHQHuBojTynhMxIkx3PV5thIIWRygq_HqkbwSjBA6JYHA-EI_ede8qD7JXZo862ac9bssEqZzxJSPJww-ypjJdioFGwP6r8WjOZDInN-_ISH5kKWWTKNAJq7Enr8_F5InCyvj_gltuftQDsG4SiljmECK3T6YsL5-DG2zdHTnHf3uJsahBpMHEqD63ULxqiSZFXsWaNFRLEBHpWL9xCrfc1ZyVmw296ZGAOBT_q8u7IONKrAg8_fYp4NIucYk8Kwp5LJcF1-fcieNCbnu_vH4swcrMDHh4GEo6ts5iszpz9BYfoEvy2NmLSIlEJykDLdJjuBMwYnqDUSKtvwMiF59QGu7lZ23c59qttLUGfBqS1tPn03pmQ4n7uLPQ49gGiLCoQUbJ4D6pmhEV5v88SEaGGVeyZGXQ-IaCnF6TJY4Of3Ga83LImvGAePBC0AQ')

# লিংক রূপান্তর ফাংশন
def convert_to_raw_link(shared_link):
    return shared_link.replace('dl=0', 'raw=1')

# নির্দিষ্ট প্যাটার্ন অনুযায়ী ফাইলের নাম তৈরি করার ফাংশন
def generate_filename(extension):
    pattern = "XXOO-OOXX-XOXO-XXXO-OOOX"
    filename = ""
    
    for char in pattern:
        if char == 'X':
            filename += random.choice(string.ascii_uppercase)  # বড় হাতের ইংরেজি অক্ষর
        elif char == 'O':
            filename += random.choice(string.digits)  # সংখ্যা (0-9)
        else:
            filename += char  # ড্যাস (-) রেখে দাও
    
    return filename + extension
# লিংক সংরক্ষণ ফাংশন
def save_link_to_json(filename, local_url, dropbox_url):
    json_file = "links.json"
    
    # আগের ডেটা লোড করার চেষ্টা
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    # নতুন তথ্য সংযোজন
    data.append({"filename": filename, "url": local_url, "dropbox_url": dropbox_url})

    # JSON ফাইল আপডেট করা
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# ড্রপবক্স থেকে ফাইল ডাউনলোড ফাংশন
def download_from_dropbox(dropbox_url, filename):
    local_filepath = os.path.join(UPLOAD_FOLDER, filename)
    response = requests.get(dropbox_url)
    with open(local_filepath, 'wb') as f:
        f.write(response.content)

# সার্ভার চালু হলে ফাইল চেক ও ডাউনলোড করবে
def check_and_download_missing_files():
    json_file = "links.json"

    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                for item in data:
                    filename = item["filename"]
                    dropbox_url = item["dropbox_url"]
                    local_filepath = os.path.join(UPLOAD_FOLDER, filename)

                    # যদি ফাইল না থাকে, তাহলে ডাউনলোড করো
                    if not os.path.exists(local_filepath):
                        print(f"{filename} পাওয়া যায়নি, ড্রপবক্স থেকে ডাউনলোড করা হচ্ছে...")
                        download_from_dropbox(dropbox_url, filename)
            except json.JSONDecodeError:
                print("links.json ফাইলটি খালি বা ভুল ফরম্যাটে আছে।")

# নতুন API: `/photo` - ফাইল আপলোড করবে এবং JSON আকারে রিটার্ন করবে
@app.route('/photo', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # নির্দিষ্ট প্যাটার্ন অনুযায়ী ফাইলের নাম তৈরি করুন
        filename = generate_filename(os.path.splitext(file.filename)[1])

        # ড্রপবক্সে আপলোড করুন
        dbx.files_upload(file.read(), f'/আপলোড/{filename}')
        
        # শেয়ার করা লিংক তৈরি করুন
        shared_link = dbx.sharing_create_shared_link(f'/আপলোড/{filename}').url
        dropbox_raw_link = convert_to_raw_link(shared_link)

        # ড্রপবক্স থেকে ফাইলটি ডাউনলোড করে লোকাল সার্ভারে সংরক্ষণ করা
        download_from_dropbox(dropbox_raw_link, filename)

        # লোকাল লিংক তৈরি করা
        local_url = f'/uploads/{filename}'

        # লিংক সংরক্ষণ করা
        save_link_to_json(filename, local_url, dropbox_raw_link)

        return jsonify({
            "message": "ফাইল আপলোড সফল!",
            "filename": filename,
            "local_url": local_url,
            "dropbox_url": dropbox_raw_link
        })

# লোকাল আপলোড ফোল্ডারের ফাইল সার্ভ করার জন্য রুট
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    local_filepath = os.path.join(UPLOAD_FOLDER, filename)

    # যদি ফাইল লোকাল ফোল্ডারে না থাকে, তাহলে ড্রপবক্স থেকে পুনরায় ডাউনলোড করো
    json_file = "links.json"
    if not os.path.exists(local_filepath) and os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                for item in data:
                    if item["filename"] == filename:
                        print(f"{filename} হারিয়ে গেছে, পুনরায় ডাউনলোড করা হচ্ছে...")
                        download_from_dropbox(item["dropbox_url"], filename)
            except json.JSONDecodeError:
                print("links.json ফাইলটি খালি বা ভুল ফরম্যাটে আছে।")

    return send_from_directory(UPLOAD_FOLDER, filename)

# JSON ফাইল থেকে লিংক রিটার্ন করার জন্য API
@app.route('/api/links')
def get_links():
    json_file = "links.json"
    
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return jsonify(data)
            except json.JSONDecodeError:
                return jsonify([])
    
    return jsonify([])

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive"})

# keep_alive ফাংশন
def keep_alive():
    url = "https://nekos-photo.onrender.com/ping"  # আপনার এপ্লিকেশনের URL দিয়ে পরিবর্তন করুন
    while True:
        time.sleep(300)
        try:
            requests.get(url)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    # সার্ভার চালুর সময় চেক করো যদি কোনো ফাইল হারিয়ে যায় তাহলে পুনরায় ডাউনলোড করো
    check_and_download_missing_files()
    
    # keep_alive ফাংশনটি একটি আলাদা থ্রেডে চালানো
    threading.Thread(target=keep_alive, daemon=True).start()
    
    app.run(host='0.0.0.0', port=8000)
