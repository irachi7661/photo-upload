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
dbx = dropbox.Dropbox('sl.u.AFmVl1umAMwJgfOOyenh1vhJymYhFLW7z9k6tgZnIpdKxXie7vVGINEpVn1HvFp5Jk1q7LnHwg7YuirPe9Ca36MOd7PAzuIsd3OWyE3lCGcWVy0LWYQoXRTfAUFSHr3BRzF5D2xfPz7DA9yyotwmgZA51Rr1kxvoUR60pl1UwwaznPm360EYicaOd8NIS2TbkO6E3Fk2a9P86HNzqf2xopt-MEY4YYZU-RIEa12sp4dfHp2oTVk2Dei36zB551tIErMBEgIslCC_Nxs2S3qCu3DJClqCsiLEQJoP5DyS1aU9KdiJ60ZZYUAGP8LVGZwsLcMxHgmcmD6M0eBp0qRgHLrzjDlurMktGbyB4DPgA8eheXQwx-aea-NHzJhBN5Gnf592-ZNHBa5E7t3eTE2RRPpmyt6TYyP_807Qn69AJA1sAAertvHJaWjliJMHPOv96fnfBK2zQDxf18p6YAysycL0d3L_pCDUQPBhZSvoOJhvzEUBB2lCDt__mhslttlYo_jbMwqhJ_a-4emYI-yCNbz1NstkkTKRqtgw6yGJEaoL3ChWmqVnjwULSzVoc6etfBSyf_UeWZ_zBhmp3RhyYZYnWg234WnjZy94qpENd4OSiRAfbE-Zjq32c1lOxexH3YGM4x0qUWHnqdY2QQvLkfw5v-vfmT8XhigbT7uT9pgeDprULmUyENiEOKS34PC0EScnS9iNgX3LG_myXmw2S_kHCQCIevgNtA0_aasbMDjv9bIqj9ljL7eCm7NwoXJrXYw8aifOEeFZlKgilUmaEv9Q9KNv3BoDclcuTBRbkaqForZqnBKtZTORZr8Ciklb5LJk8CjRsyeLl5Njh6L2GBA-XStwYhytV8CzEsFd2hJxCILw0za7wJZUM05H3ymbfv0BSCbQVDGDOzv5ImmjhhTfEqzZeqw5PHEM_L9ovCqdRuPg3xHF6iavlI0NbDUdaqYissaheN2XqfUi6MptCP6oZLJKzxY95k89Q-P8XJh3JJNbjgi1FnVICLX6KEHJL7C09wjCKUmrgrIuPHq8RyKkucraCZNjvBvc2-vgOLQAwKCSCvNLVHLvwVQ6yJ_o23cjciZAk2QS5JP3VFpW3cY0d8eBz4bzaqbclExnh6NSnoCcjFMQNYEDnWO_2R6mHjVvPVu5THRzAu71DUZg5YHdHIx4WoAQDbCq5g_IdJ7V-iXKNYlPJce-5ooL3o7Rb8Ti799aZLlz4IfzaoqrZgrPbAmwt7rx9SZak-rJ-nlZuDJ1If9fRQyoVaeHhO0lkNHo4s_jSxrHLpVKxrK1rVlN0VvYauB9sN2kyFIsPNjNvtnReOg-ombJstxgakRYykj4ypbGBfdxiKrr3bEi58TPk5M-fDR458uUQZ_1eHH47w3YghXuUPTWBwZGDD4EA_XkaoK8x9KqdoI9VCuhBKoj4CrKp0yd8-HNAbnan_LSezbVT9Dci9FwQBtXO7hQWWw')

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
