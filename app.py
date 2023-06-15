from flask import Flask, render_template, request
from selenium import webdriver
from bs4 import BeautifulSoup
import pyautogui
import time
from datetime import date
import matplotlib.pyplot as plt
import os
import csv

plt.rcParams['font.family'] = 'Microsoft JhengHei'
app = Flask(__name__, static_folder='static', static_url_path='/static')


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/result", methods=['POST'])
def result():
    url = request.form['url']
    keyword1 = request.form['keyword1']
    keyword2 = request.form['keyword2']
    keyword3 = request.form['keyword3']
    keywordM = int(request.form['keywordM'])
    keywordn = int(request.form['keywordn'])
    keywordo = int(request.form['keywordo'])

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)
    pyautogui.moveTo(350, 500)
    time.sleep(1)

    num_executions = 10
    result = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    for i in range(num_executions):
        pyautogui.scroll(-100000)
        time.sleep(0.5)
        pyautogui.scroll(800)

    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    review = soup.select('span.iUtr1.CQYfx,div.STQFb.eoY5cb')

    article_texts = []
    for i in range(0, len(review), 2):
        text1 = review[i].text
        text2 = review[i+1].text if i+1 < len(review) else ''
        combined_text = text1 + ' ' + text2
        article_texts.append(combined_text)

    today = date.today()
    month = today.month

    keywordM = calculate_month_diff(month, keywordM)
    keywordn = calculate_month_diff(month, keywordn)
    keywordo = calculate_month_diff(month, keywordo)

    keyword1_counts = []
    keyword2_counts = []
    keyword3_counts = []

    for text in article_texts:
        if str(keywordM) in text or str(keywordn) in text or str(keywordo) in text:
            count = text.count(keyword1)
            keyword1_counts.append(count)

    for text in article_texts:
        if str(keywordM) in text or str(keywordn) in text or str(keywordo) in text:
            count = text.count(keyword2)
            keyword2_counts.append(count)

    for text in article_texts:
        if str(keywordM) in text or str(keywordn) in text or str(keywordo) in text:
            count = text.count(keyword3)
            keyword3_counts.append(count)

    # Prepare the keyword counts
    keyword1_count = sum(keyword1_counts)
    keyword2_count = sum(keyword2_counts)
    keyword3_count = sum(keyword3_counts)

    # Generate and save the chart
    keywords = [f'{keyword1}', f'{keyword2}', f'{keyword3}']
    counts = [keyword1_count, keyword2_count, keyword3_count]

    fig, ax = plt.subplots()
    ax.bar(keywords, counts)
    ax.set_ylabel('Count')
    ax.set_title('Keyword Counts')
    ax.set_xticklabels(keywords, rotation=45, ha='right')
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    tmp_filename = './static/plot.jpg'
    plt.savefig(tmp_filename)



    # Prepare keyword comments for CSV export
    keyword1_comments = []
    keyword2_comments = []
    keyword3_comments = []

    for text in article_texts:
        if str(keywordM) in text or str(keywordn) in text or str(keywordo) in text:
            if keyword1 in text:
                keyword1_comments.append(text)
            if keyword2 in text:
                keyword2_comments.append(text)
            if keyword3 in text:
                keyword3_comments.append(text)


    # Save keyword comments to CSV files
    save_comments_to_csv(keyword1_comments, './static/keyword1_comments.csv')
    save_comments_to_csv(keyword2_comments, './static/keyword2_comments.csv')
    save_comments_to_csv(keyword3_comments, './static/keyword3_comments.csv')

    # Render the result template with the keyword counts and chart image file
    # Render the result template with the keyword counts and chart image file
    return render_template('result.html', keyword1=keyword1, keyword2=keyword2, keyword3=keyword3,image_file=tmp_filename, keyword1_count=keyword1_count, keyword2_count=keyword2_count,keyword3_count=keyword3_count)


def calculate_month_diff(current_month, target_month):
    if target_month > current_month:
        return str(12 + current_month - target_month) + ' 個月前'
    elif target_month < current_month:
        return str(current_month - target_month) + ' 個月前'
    else:
        return str(0) + ' 個月前'

def save_comments_to_csv(comments, filename):
    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Comments'])
        for comment in comments:
            writer.writerow([comment])


if __name__ == "__main__":
    app.run()
