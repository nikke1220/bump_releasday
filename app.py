from flask import Flask, render_template, request
import csv
from datetime import datetime

app = Flask(__name__)

def load_releases():
    releases = []
    with open('releases.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # 年月日を整数にしておくと並び替えやすい
            row['year'] = int(row['year'])
            row['month'] = int(row['month'])
            row['day'] = int(row['day'])
            releases.append(row)
    return releases

def sort_releases(releases, sort_key):
    if sort_key == 'oldest':
        return sorted(releases, key=lambda x: (x['year'], x['month'], x['day']))
    elif sort_key == 'title':
        return sorted(releases, key=lambda x: x['title'])
    else:
        return releases

@app.route('/')
def index():
    sort = request.args.get('sort', 'default')
    releases = load_releases()
    releases = sort_releases(releases, sort)
    return render_template('list.html', releases=releases, sort=sort)

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    keyword = ''
    sort = request.args.get('sort', 'default')
    if request.method == 'POST':
        keyword = request.form['keyword'].lower()
        with open('releases.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                title = row['title'].lower()
                date_str = f"{row['year']}-{row['month']}-{row['day']}"
                if keyword in title or keyword in date_str:
                    row['year'] = int(row['year'])
                    row['month'] = int(row['month'])
                    row['day'] = int(row['day'])
                    results.append(row)
        results = sort_releases(results, sort)
    return render_template('search.html', results=results, keyword=keyword, sort=sort)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/search_date', methods=['GET', 'POST'])
def search_date():
    results = []
    if request.method == 'POST':
        try:
            y = int(request.form['year'])
            m = int(request.form['month'])
            d = int(request.form['day'])
            input_date = datetime(y, m, d)
        except ValueError:
            # 無効な日付入力の処理
            return render_template('search_date.html', results=[], error="正しい日付を入力してください")

        # CSV読み込み＆日付差を計算し、最も近いリリースを探す
        with open('releases.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            # 日付の差と行をセットで記録
            date_diffs = []
            for row in reader:
                try:
                    row_date = datetime(int(row['year']), int(row['month']), int(row['day']))
                    diff = abs((row_date - input_date).days)
                    date_diffs.append((diff, row))
                except Exception:
                    continue

            if date_diffs:
                # 差が最小のものを取得
                min_diff = min(date_diffs, key=lambda x: x[0])[0]
                # 差が最小のものをすべて取得（同日や同距離の場合）
                results = [r for diff, r in date_diffs if diff == min_diff]
            else:
                results = []

    return render_template('search_date.html', results=results)
