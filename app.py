from flask import Flask, render_template, url_for, request, redirect  #render_template umożliwia nam korzystanie z templatków
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField , BooleanField   # bo nasz formularz wtf będzie miał pola string
import mysql.connector
import requests
import bs4
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)  # __name__ oznacza, że jest to ta strona jest do zarządzania, tworzymy instancję klasy flaskowej
app.config['SECRET_KEY'] = 'AComplicat3dTest.'

mydb = mysql.connector.connect(user='root', password='adminadmin', host='127.0.0.1', database='my_project')
mycursor = mydb.cursor()


class BookForm(FlaskForm):

    title = StringField('Book title')
    amount = IntegerField('Amount')
    available = BooleanField('Available')
def pokaz_kurs(sql):
  mycursor.execute(sql)
  myresult = mycursor.fetchall()
  kursy=[]
  for x in myresult:
    kurs=[x[0],x[1],x[2],x[3]]
    kursy.append(kurs)
    print(str(x[0])+" USD, ",str(x[1])+" PL, -> ",x[2],x[3])
  print(myresult)
  return kursy

def pobiez():
  url = 'https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=ZLOTO'
  try:
    page = requests.get(url)
    page.raise_for_status()
  except Exception as exc:
    print("wystąpił błąd: %s" % (exc))
    print(f"sprawdź czy adres strony {url} został wpisany poprawnie")

  soup = bs4.BeautifulSoup(page.content, 'html.parser')
  find_gold_rate = soup.find('div',
                             {'class': "profilLast"})  # znajdzie tag '<div>' mający jako atrybut class=profilLast
  gold = find_gold_rate.getText()  # zapisze zawartość tagu w zmiennej 'gold'
  gold_rate = gold[:1] + gold[2:5] + '.' + gold[6:8]

  find_pl = soup.find_all('span', {'class': 'value'})
  gold_rate_pl = find_pl[4].getText().strip()
  gold_rate_pl = gold_rate_pl[0] + gold_rate_pl[2:]
  gold_rate_pl = gold_rate_pl[:4] + '.' + gold_rate_pl[5:]
  return gold_rate, gold_rate_pl

def wstaw_kurs(kurs_pl, kurs_usd, mydb):
  sql=f"INSERT INTO kursy(kursy_pl, kursy_usd, data, godzina) VALUES ({str(kurs_pl)}, {str(kurs_usd)}, CURDATE(), CURTIME())"
  cursor = mydb.cursor()
  cursor.execute(sql)
  mydb.commit()

def wykres_zlota():
    my_data = pd.read_sql("SELECT * FROM kursy", mydb)
#    gold_rate = pd.read_csv('zloto.csv', sep=';', index_col=['data', 'godzina'], header=0)  # index_col - co ma być indeksem
    print(my_data)
    df = pd.DataFrame(my_data)
    return df
@app.route('/', methods=['GET','POST'])     #tu będzie z obsługą flask_wtf
def index():

    # list = pokaz("SELECT * FROM kursy")
    # print(list)
    # return render_template('index.html')
    return render_template('index.html')
@app.route('/wstaw')
def wstaw():

    kurs = pobiez()
    wstaw_kurs(kurs[1], kurs[0], mydb)
    return render_template('wstaw2.html', kurs=kurs)

@app.route('/aktualny')
def aktualny():

    kurs = pobiez()
    wstaw_kurs(kurs[1], kurs[0], mydb)
    return render_template('aktualny2.html', kurs=kurs)
@app.route('/pokaz')
def pokaz():
    list = pokaz_kurs("SELECT * FROM kursy")
    print(list)
    return render_template('pokaz2.html', list=list)
@app.route('/wykres')
def wykres():
    my_data = pd.read_sql("SELECT * FROM kursy", mydb, index_col=['data', 'godzina'])
    df = pd.DataFrame(my_data, columns=['kursy_pl', 'kursy_usd'])
#    df.plot(figsize=(13,5), title="cos tam", subplots=True, linestyle='-.', xticks=(range(30)), grid=True, rot=45 )
    df.plot(figsize=(13, 5), title="Kurs złota", subplots=True, linestyle='-.', grid=True, rot=45)


    for ax in plt.gcf().axes:
        ax.legend(loc=1)
    plt.show()
    return render_template('wykres.html')


#    return render_template('pokaz.html', list=list)
if __name__ == '__main__':
    app.run()



if __name__ == '__name__':   # to umożliwia uruchomienie programu przez wpisanie w terminalu python app.py
    app.run()                # przy uruchamianiu przez flusk run  te dwie linijki nie są potrzebne

