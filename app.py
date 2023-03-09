from flask import Flask, render_template, url_for, request  #render_template umożliwia nam korzystanie z templatków
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField , BooleanField   # bo nasz formularz wtf będzie miał pola string
import mysql.connector
import requests
import bs4

app = Flask(__name__)  # __name__ oznacza, że jest to ta strona jest do zarządzania, tworzymy instancję klasy flaskowej
app.config['SECRET_KEY'] = 'AComplicat3dTest.'

mydb = mysql.connector.connect(user='root', password='adminadmin', host='127.0.0.1', database='my_project')
mycursor = mydb.cursor()


class BookForm(FlaskForm):

    title = StringField('Book title')
    amount = IntegerField('Amount')
    available = BooleanField('Available')
def pokaz(sql):
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

def wstaw(kurs_pl, kurs_usd, mydb):
  sql=f"INSERT INTO kursy(kursy_pl, kursy_usd, data, godzina) VALUES ({str(kurs_pl)}, {str(kurs_usd)}, CURDATE(), CURTIME())"
  cursor = mydb.cursor()
  cursor.execute(sql)
  mydb.commit()

@app.route('/', methods=['GET','POST'])     #tu będzie z obsługą flask_wtf
def index():
    
    # form = BookForm()
    #
    # if form.validate_on_submit():     # jeśli tak funkcja jest true to znaczy, że user przesłał nam w miarę poprawne dane
    #     return f'''   <h1>Dane</h1>
    #         <ul>
    #             <ol> {form.title.label}:{form.title.data}</ol>
    #             <ol> {form.amount.label}:{form.amount.data}</ol>
    #             <ol> {form.available.label}:{form.available.data}</ol>
    #         </ul>
    #
    #
    #     '''

#    kurs = pobiez()
 #   wstaw(kurs[1], kurs[0], mydb)
    list = pokaz("SELECT * FROM kursy")
    print(list)
    return render_template('index.html', list=list)


if __name__ == '__main__':
    app.run()

@app.route('/wstaw')
def wstaw():

    kurs = pobiez()
    wstaw(kurs[1], kurs[0], mydb)
    return render_template('wstaw.html')

@app.route('/exchange', methods=['GET','POST'] )   # to do formularza templatka i obsluga bez flask_wtf
def exchange():
    if request.method=='GET':
        return render_template('exchange.html')
    else:
        currency = 'EUR'
        if 'currency' in request.form:
            currency = request.form['currency']
        
        amount = 100
        if 'amount' in request.form:
            amount = request.form['amount']
        
        name="Nie podane"
        if 'name' in request.form:
            name = request.form['name']

        return render_template('result.html', currency=currency, amount=amount, name=name)




if __name__ == '__name__':   # to umożliwia uruchomienie programu przez wpisanie w terminalu python app.py
    app.run()                # przy uruchamianiu przez flusk run  te dwie linijki nie są potrzebne

