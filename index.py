from flask import Flask, render_template, request
from dodaxprocessor import Threading
import time

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        start = time.perf_counter()

        artist = request.form['artist']
        title = request.form['title']
        if not artist and not title:
            return render_template("index.html", feedback="Please fill in the form.")
        elif not request.form['format'] or not request.form['format']:
            return render_template("index.html", feedback="Please state a currency or format.", artist=artist, title=title)
        elif request.form['format'] != 'CD' and request.form['format'] != 'Vinyl':
            return render_template("index.html", feedback="Don't try to hack me.", artist=artist, title=title)
        elif request.form['currency'] != 'EUR' and request.form['currency'] != 'GBP' and request.form['currency'] != 'CHF' and request.form['currency'] != 'PLN':
            return render_template("index.html", feedback="Don't try to hack me.", artist=artist, title=title, format=request.form['format'])
        else:
            search = " ".join([request.form["artist"], request.form["title"]])
            SoupString = "+" + search.lower().replace(" ", "+") + "+" + request.form['format']
            SoupString = SoupString.replace("+a+", "+").replace("+the+", "+").replace("++", "+") # Delete 'The' and 'A' for better search results
            content = Threading(SoupString[1:], artist, title, request.form['currency']) # returns list
            print(SoupString[1:])

            if not content:
                feedback = 'Release not found in any shop.'
            else:
                feedback = search +" "+ request.form['format']

            finish = time.perf_counter()
            print(f'Finished in {round(finish-start, 2)} seconds(s)')
            return render_template("index.html", feedback=feedback,
                                                  content=content,
                                                  artist=artist,
                                                  title=title,
                                                  format=request.form['format'],
                                                  cur=request.form['currency'])
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
