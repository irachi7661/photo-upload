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
dbx = dropbox.Dropbox('sl.u.AFnxZHyB8c0wqCUFIdcGPZohgK9h45ab-ONjlHt1OiGxyoGAdK58XmZhvpJsGopQGUa5xH52-ez7fKpBlIL8kb-iHUIEoBguOTez_7ByL16Q1509Wu1VYiTuP2Ow6MrvRrQwoAMnDcMb9Pm-jXjbfRmJ6jwPqkjEy7VDaYxsXbO8UFHApZJyWYP7PuNF3jTbSvo1wIzvBBED1oikVrMa2tvdGkdZojbJfyNIpHjSvhGCY8QEvCrSsraL0xuS3v36Zyc3wHPG1jeuRL4UJnTRC_aMshKoMvRlSgEGxui9x7MX7sUvv8kXEWrAdq2LVOxcY2shtYZQdZi5U6x7yCi2YFC_FQbndyEag8R1TIJlVwVdtc6FRIxXppykWiqHH3nllTBDDGVGIFlYCg1q91Tsjvo1UUGCXysNcefw773kXsQOB0wL-s6Gq6kozbAywauWYgr0f2x9C8_YJfaHW27fT8nkHbYXXcWEI_rYqcOYsu3G-DS6U4o2vsD9cf2xwPhNqUl1QKWgGbwaSomO_Rl34GY3DyMw2Kz7OBU_VWaCgQlUvTYOZzGFlH1UmSRCf-bgviR3M2IsK7DD4vhQcnmVCzYGV-VazucWaGWV5ZloWbPEvSGxC3Q6X9mrbLomcg2Vyb0o8j7ttaqjL8c4Pi78Bv-ipel96P6zVn-397hEabnGBpVl3koaSi2atQt5ouumtbicnlT1HCuhi9cW0F4n4rvjPh713xH2UWrNGf8zg6ASnIymcd5jZYBVkDDOh2K5pgtQPJcKz_4t49lhpJIAV5ZMZYdLPoCYrWvIKWLyLZVhvDreUQ_gNK1inDaN6UzUqUpEB-fQ2L5Y8PemulH37v3Ny1XdZBUYHhiVbjO092umKxX9EVR-B6vLpHe2d0irEXKrwYFJjfG26fS-Jw1ol1vBYWQn-2PvYfjMRWZJGZ7uyL_O-NFxEuLFo1kMr9x7sguI1bkONL7gtHo-u_Tk13a-szY2y9IDfHeIEB86meeHYZ6pSQoiqZjHmKLmNp41a8j0mHaePbJShdFqVrp0682UgvhlV_zgIadmEmVpSM2sURpBSuzYJ8Po1SgbzPEOkvvAsp3wvdazvCCLb6948lFHHIfpAmOQaW72iCeDOH7r70Xn7MBI0d1uqdnDLl9v20_ryMFhmYPIP6JyxcCbCA37NhGIdACru1V7qNo_jH8bqXxVTxBIUlTWw0iWRblMfNsw_2UqJFAMiibJpA23j-ZqqguH4OZPsoZaZcWAgxy3Mz8mac0GHfABO014JzjI66AF1baxMCcQmWVdTn5vXUMqlxgSCQQ4EZ1UTt0m4DGFLUMhpl5vbl9Xbq5GXTTWUSsPhjV9r9B4x6KTfpV9Fv6IhKQul40bg4R9yf5Er5_LoLZ2k-nfT2AIa9mPrSiVvZKGpn8cogf2TY4b5kQKlsKCTUG1oN7GSMxswHxUNFMl6DJtuU81EKtD4ZuPPnWsnT0')

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
