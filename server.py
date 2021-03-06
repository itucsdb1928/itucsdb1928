from flask import Flask, redirect, render_template,flash,url_for,current_app,request
from forms import RegistrationForm,LoginForm,AddUserContent,editPublisher,editAuthor,editProfile

from datetime import datetime
from urllib.parse import urlparse
import os
import psycopg2 as dbapi2
from arrangement import Database
from datetime import date
from cyripto import Crypto

app = Flask(__name__)
db=Database()
crp = Crypto()
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route('/')
@app.route('/Home',methods=['GET','POST'])
def homepage():
    My_list = []
    if request.method == "POST":
        if request.form["btn"] == "search":
            db.book_name=request.form["search_book"]
            My_list=db.Search(db.book_name)
        elif request.form["btn"] == "detail":
            db.book_name=request.form["Book_name"]
            db.book_detail=db.get_detail_page(db.book_name)
            return redirect(url_for('detail_page'))
        elif request.form["btn"] == "add_book":
            return redirect(url_for('add_book'))
        elif request.form["btn"] == "add_author":
            return redirect(url_for('add_author'))
        elif request.form["btn"] == "add_publisher":
            return redirect(url_for('add_publisher'))
    else:
        My_list=db.get_home_page()
    return render_template('home.html',Status =db.UserId,title = "Home Page",titles=My_list,user=db.UserId)


@app.route('/Add_Book',methods=['GET','POST'])
def add_book():
    if request.method == "POST":
        if request.form["btn"] == "cancel":
            return redirect(url_for('homepage'))
        elif request.form["btn"] == "add_book":
            title=request.form["title"]
            postdate=request.form["postdate"]
            PageNum=request.form["PageNum"]
            content=request.form["content"]
            authorid=request.form["Authorid"]
            publisherid=request.form["Publisherid"]
            db.add_new_book(title, postdate, PageNum, content, authorid, publisherid)

            return redirect(url_for('homepage'))


    return render_template('add_book.html', Status=db.UserId, title="New Book Page",publisher=db.all_publishers(),author=db.all_authors())

@app.route('/Add_Author',methods=['GET','POST'])
def add_author():
    Country = "Universe"
    if request.method == "POST":
        if request.form["btn"] == "cancel":
            return redirect(url_for('homepage'))
        elif request.form["btn"] == "add_author":
            name = request.form["name"]
            surname = request.form["surname"]
            birthdate = request.form["birthdate"]
            numberofbooks = request.form["numberofbooks"]
            Country = request.form["country"]
            db.add_new_author(name,surname, birthdate, numberofbooks, Country)

            return redirect(url_for('homepage'))


    return render_template('add_author.html', Status=db.UserId, title="New Author Page",country=Country)

@app.route('/Add_Publisher',methods=['GET','POST'])
def add_publisher():
    if request.method == "POST":
        if request.form["btn"] == "cancel":
            return redirect(url_for('homepage'))
        elif request.form["btn"] == "add_publisher":
            name = request.form["name"]
            adress = request.form["adress"]
            numberOfbooks = request.form["numberofbooks"]
            establishmentdate = request.form["establismentdate"]
            companyName = request.form["companyname"]
            db.add_new_publisher(name,adress,numberOfbooks, establishmentdate, companyName)

            return redirect(url_for('homepage'))


    return render_template('add_publisher.html', Status=db.UserId, title="New Publisher Page")


@app.route('/SignIn',methods=['GET','POST'])
def sign_in_page():
    db.UserId= 0
    form = LoginForm()
    if form.validate_on_submit():
        db.UserId = db.checkLogin(form.email.data,form.password.data)
        if db.UserId > 0:
            flash('Başarılı bir şekilde giriş yaptınız!', 'success')
            return redirect(url_for('profile_page'))
    
    return render_template('login.html',Status =db.UserId,title = "SıgnIn Page", form=form)

@app.route('/SignUp',methods=['GET','POST'])
def sign_up_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        print("submited")
        form.password.data = crp.password2secret(form.password.data)
        db.UserId = db.insertNewUser(form)
        if db.UserId > 0:
            flash('Başarılı bir şekilde giriş yaptınız!', 'success')
            return redirect(url_for('profile_page'))

    return render_template('register.html', Status=db.UserId, title="SıgnUp Page", form=form)




@app.route('/Profile',methods=['GET','POST'])
def profile_page():
    addNewContent = 0
    profile=db.show_profile(db.UserId)
    if (len(profile) == 5):
        addNewContent = 1
    print("------new cont:",addNewContent)
    if request.method == "POST":
        if request.form["btn"] == "edit_profile" :
            return redirect(url_for('edit_profile_page'))
        elif request.form["btn"] == "edit_userContent":
            return redirect(url_for('edit_user_content'))
        if request.form["btn"] == "add_content":
            return redirect(url_for('add_user_content'))

    return render_template('profile.html', Status=db.UserId, title = "Profile Page", profile=profile,addContent = addNewContent)


@app.route('/EditProfile',methods=['GET','POST'])
def edit_profile_page():
    profile = db.show_profile(db.UserId)
    print(profile)
    form = editProfile()
    if request.method == "POST":
        if form.validate_on_submit():
            db.edit_profile(form.name.data, form.surname.data, form.age.data, form.gender.data, db.UserId)
            return redirect(url_for('profile_page'))
        if request.form["btn"] == "cancel" :
            return redirect(url_for('profile_page'))
        elif request.form["btn"] == "delete":
            db.delete_profile(db.UserId)
            db.UserId = 0
            return redirect(url_for('sign_up_page'))

    return render_template('edit_profile.html', Status=db.UserId, title="Edit Profile Page", profile=profile,form=form)

@app.route('/EditUserContent',methods=['GET','POST'])
def edit_user_content():
    profile = db.show_profile(db.UserId)
    print(profile)
    form = AddUserContent()
    if request.method == "POST":
        if form.validate_on_submit():
            print("buradayımmmmm------------------------")
            print("Edit part---->",form.author.data)
            db.edit_user_content(form)
            return redirect(url_for('profile_page'))
        elif request.form["btn"] == "delete":
            db.delete_user_content()
            return redirect(url_for('profile_page'))
        elif request.form["btn"] == "cancel" :
            print("-------->print:",request.form)
            return redirect(url_for('profile_page'))

    return render_template('edit_user_content.html', Status=db.UserId, title="Edit Profile Page", profile=profile,form=form)

@app.route('/AddingUserContent',methods=['GET','POST'])
def add_user_content():
    form = AddUserContent()
    if request.method == "POST":
        if form.validate_on_submit():
            db.NewContent(form)
            return redirect(url_for('profile_page'))
        elif request.form["btn"] == "cancel":
            return redirect(url_for('profile_page'))
    return render_template('add_content.html', Status=db.UserId, title="Add Content",form=form)

@app.route('/EditAuthor',methods=['GET','POST'])
def edit_author_page():
    form = editAuthor()
    if request.method == "POST":
        if form.validate_on_submit():
            db.edit_author(form.name.data, form.surname.data,form.date.data,form.numOfBooks.data,form.country.data, db.author_details[5])
            return redirect(url_for('homepage'))
        elif request.form["btn"] == "cancel":
            return redirect(url_for('author_detail_page'))
        elif request.form["btn"] == "delete_author":
            db.delete_author(db.author_details[5])
            return redirect(url_for('homepage'))

    return render_template('edit_author.html', Status=db.UserId, title="Edit Author Page",author=db.author_details,user=db.UserId,form=form)

@app.route('/EditPublisher',methods=['GET','POST'])
def edit_publisher_page():
    print(db.publisher_details[4])
    form = editPublisher()
    if request.method == "POST":
        if form.validate_on_submit():
            db.edit_publisher(form.name.data, form.address.data, form.numOfBooks.data, form.date.data, form.companyName.data, db.publisher_details[4])
            return redirect(url_for('homepage'))
        elif request.form["btn"] == "cancel":
            return redirect(url_for('publisher_detail_page'))
        elif request.form["btn"] == "delete_publisher":
            db.delete_publisher(db.publisher_details[4])
            return redirect(url_for('homepage'))

    return render_template('edit_publisher.html', Status=db.UserId, title="Edit Publisher Page",publisher=db.publisher_details, name=db.book_detail[2],user=db.UserId,form=form)

@app.route('/Author_Profile',methods=['GET','POST'])
def author_detail_page():
    nameAuthor=db.book_detail[0]
    surnameAuthor=db.book_detail[1]
    if request.method == "POST":
        if request.form["btn"] == "update_author":
            return redirect(url_for("edit_author_page"))


    return render_template('detail_author.html',Status =db.UserId, title="Author Detail Page",author=db.author_details, name=nameAuthor,surname=surnameAuthor,user=db.UserId)

@app.route('/Publisher_Profile',methods=['GET','POST'])
def publisher_detail_page():
    if request.method == "POST":
        if request.form["btn"] == "update_publisher":
            return redirect(url_for("edit_publisher_page"))
    return render_template('detail_publisher.html',Status =db.UserId, title="Edit Publisher Page",publisher=db.publisher_details, name=db.book_detail[2],user=db.UserId)

@app.route('/Detail',methods=['GET','POST'])
def detail_page():
    bookId = db.book_detail[5]
    today = date.today()
    bookRateInfo = db.getReview(bookId)
    detailStat = db.UserId
    commentCheck = db.checkUser(db.UserId,bookId)

    if(commentCheck == False):
        detailStat = -1

    if request.method == "POST":
        if request.form["btn"] == "ratingBtn" :
            userWiev = request.form
            print(userWiev)
            today = today.strftime("%m/%d/%Y")
            result = db.insertRate(db.UserId,bookId,userWiev,today)
            if(result):
                return redirect(url_for('detail_page'))
        elif request.form["btn"] == "updateBtn" :
            newContent = request.form['comment']
            db.updateBookContent(bookId,newContent)
            return redirect(url_for('homepage'))
        elif request.form["btn"] == "delete_book":
            db.delete_book(bookId)
            return redirect(url_for('homepage'))
        elif request.form["btn"] == "1":
            print("ım here",request.form["custId"])
            db.updateLike(request.form["custId"],"like")
            return redirect(url_for('detail_page'))
        elif request.form["btn"] == "-1":
            db.updateLike(request.form["custId"],"dislike")
            return redirect(url_for('detail_page'))
        elif request.form["btn"] == "delete_comment":
            db.delete_comment(bookId)
            return redirect(url_for('detail_page'))
        elif request.form["btn"] == "detail_p_a":
            if request.form['radiobutton']=='author':
                db.author_details=db.show_author_detail(db.book_detail[0],db.book_detail[1])
                return redirect(url_for('author_detail_page'))
            else:
                db.publisher_details=db.show_publisher_detail(db.book_detail[2])
                return redirect(url_for('publisher_detail_page'))

            
    return render_template('detail.html',Status=detailStat,user=db.UserId,title = " %s Detail Page"%(db.book_name),details=db.book_detail,
                           name=db.book_name,rateInfo = bookRateInfo,today=today) 

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

