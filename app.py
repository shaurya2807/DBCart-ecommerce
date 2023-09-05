from flask import Flask, render_template, request, flash, url_for, redirect
from flask_mysqldb import MySQL
import random


app = Flask(__name__)

app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']="password"
app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_DB']="ecommerce"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = "super secret"

product_id = 0
order_id = 0

mysql = MySQL(app)



@app.route("/customer/<cid>", methods=['GET', 'POST'])
def customer(cid):
    cur = mysql.connection.cursor()
    fresult = []
    cur.execute("SELECT * FROM _order INNER JOIN shipping ON _order.order_id=shipping.order_id;")
    orders = cur.fetchall()
    for i in range(len(orders)):
        if(orders[i]['c_id']==cid):
            fresult.append(orders[i])
    
    if request.method == "POST":
        if request.form['aud'] == 'updateCustomer':
            customer_first_name = request.form['First_name']
            customer_last_name = request.form['Last_name']
            pincode = request.form['Pincode']
            ph_num = request.form['Phone_num']
            email = request.form['email']
            add_line1 = request.form['add_line1']
            add_line2 = request.form['add_line2']
            city = request.form['city']
            cur.execute(f"update personal_info set first_name = '{customer_first_name}', last_name = '{customer_last_name}', add_line1 = '{add_line1}', add_line2 = '{add_line2}', city = '{city}', pincode = '{pincode}', ph_no = '{ph_num}', email_id = '{email}' where username='{cid}'")
            cur.connection.commit()
        if request.form['aud'] == 'prod':
            return redirect(url_for('products', cid = cid))
    cur.close()
    return render_template('customer.html', cid = cid, orders = fresult)

@app.route("/",methods=["GET","POST"])
def hello_world():
    cur = mysql.connection.cursor()
    if request.method=='POST':
        if request.form['login/signup'] == 'login':
            entered_username = request.form['username']
            entered_pass = request.form['pass']
            entered_type = request.form['options']
            cur.execute(f"select exists(select * from user where username='{str(entered_username)}' and passwd='{str(entered_pass)}' and _type = '{str(entered_type)}')")
            result = cur.fetchall()
            first_value = list(result[0].items())[0][1]
            if first_value==1:
                if entered_type == 'C':
                    return redirect(url_for('customer', cid = entered_username))
                else:
                    return redirect(url_for('seller', sid = entered_username))
            else:
                flash("Incorrect Username/Password")
        elif request.form['login/signup'] == 'signup':
            user_type = request.form['options']
            user_username = request.form['Username']
            user_password = request.form['Password']
            user_first_name = request.form['First_name']
            user_last_name = request.form['Last_name']
            pincode = request.form['Pincode']
            ph_num = request.form['Phone_num']
            email = request.form['email']
            add_line1 = request.form['add_line1']
            add_line2 = request.form['add_line2']
            city = request.form['city']
            cur.execute(f"insert into user (username, _type, passwd) values ('{user_username}', '{user_type}', '{user_password}')")
            # trigger to add in customer and seller table
            cur.execute(f"insert into personal_info (first_name, last_name ,username, add_line1, add_line2, city, pincode, ph_no, email_id) values ('{user_first_name}', '{user_last_name}', '{user_username}', '{add_line1}', '{add_line2}', '{city}', '{pincode}', '{ph_num}', '{email}')")
            cur.connection.commit()
    cur.close()
    return render_template('homepage.html')

@app.route('/products/<cid>', methods=['GET', 'POST'])
def products(cid):
    cur = mysql.connection.cursor()
    cur.execute("select * from product")
    results = cur.fetchall()
    if request.method=='POST':
        
        if request.form['action1']  == 'filter':           
            if(str(request.form.get('filter'))!= 'None'):
                filter = request.form.get('filter')
                if (filter == "1"):
                    cur.execute("select  * from product order by price DESC")
                    results = cur.fetchall()
                elif (filter == "2"):
                    cur.execute("select  * from product order by price ASC")
                    results = cur.fetchall()
                elif (filter == "3"):
                    cur.execute("select * from product where stock<>0")
                    results = cur.fetchall()  
                elif (filter == "4"):
                    cur.execute("SELECT * FROM product ORDER BY p_name ASC")
                    results = cur.fetchall()      
                         

        elif request.form['action1'] == 'cart':
            return redirect(url_for('cart', cid = cid))    
        else:
            quantity = 1
            if(str(request.form.get('quantity'))!= 'None'):
                quantity = request.form.get('quantity')
            cur.execute(f"select count(*) from cart where p_id = '{request.form['action1']}' and c_id = '{cid}'")
            cc = cur.fetchall()
            if cc[0]['count(*)']>0:
                cur.execute(f"update cart set quantity=quantity+{quantity} where c_id='{cid}' and p_id='{request.form['action1']}'")
            else:
                cur.execute(f"insert into cart (p_id, c_id, quantity) values ('{request.form['action1']}', '{cid}', '{quantity}')")
            cur.connection.commit()
        
    cur.close()
    return render_template('products.html', products = results, cid = cid)

@app.route("/cart/<cid>", methods=['GET', 'POST'])
def cart(cid):
    cur = mysql.connection.cursor()
    cur.execute(f"select * from cart where c_id = '{cid}'")
    results = cur.fetchall()
    lis = []
    for el in results:
        cur.execute(f"select * from product where p_id = '{el['p_id']}'")
        results2 = cur.fetchall()
        results2[0]['quantity'] = el['quantity']
        lis.append(results2)
    cur.execute(f"select sum(quantity*(select price from product where cart.p_id=product.p_id)) from cart where c_id='{cid}'")
    results3 = cur.fetchall()
    total_price = list(results3[0].items())[0][1]
    cur.execute(f"Select count(distinct p_id) as dist_prod from cart where c_id='{cid}'")
    results4 = cur.fetchall()
    total_items = results4[0]['dist_prod']
    if request.method == "POST":
        if request.form['del'] == "Checkout":
            cur.execute(f"insert into _order (payment_type, c_id, total_cost) values ('O', '{cid}', '{total_price}')")
            cur.connection.commit()

            # cur.execute(f"INSERT INTO history(quantity, order_date, p_id, c_id, order_id,_status) values ((select quantity from cart where cart.c_id='{cid}'), CURDATE(), (select p_id from cart where cart.c_id='{cid}'),'{cid}', (select order_id from _order where c_id='{cid}'),'temp');")
            # cur.connection.commit()
            cur.execute(f"SELECT order_id as maxOID FROM _order ORDER BY order_id DESC LIMIT 0, 1")
            res = cur.fetchall()
            oid = res[0]['maxOID']
            lis = []
            cur.execute(f"select * from cart where c_id = '{cid}'")
            res = cur.fetchall()
            for temp in res:
                lis.append({'p_id': temp['p_id'], 'quantity': temp['quantity']})
            for temp in lis:
                cur.execute(f"insert into history values ('{temp['quantity']}', '2022-06-21' , '{temp['p_id']}', '{cid}', '{oid}', 'DELIVERING')")
                cur.connection.commit()
            # cur.execute(f"delete from cart where c_id = '{cid}'")
            # cur.connection.commit()
            cur.close()
            return redirect(url_for('checkout', oid = oid))
        else:
            tobedel = request.form['del']
            cur.execute(f"delete from cart where c_id='{cid}' and p_id='{tobedel}'")
            cur.connection.commit()
            cur.close()
            return redirect(url_for('cart', cid = cid))
    cur.close()
    return render_template('cart.html', cid = cid, prodList = lis, total_price = total_price, total_items = total_items)

@app.route("/checkout/<oid>", methods=['GET', 'POST'])
def checkout(oid):
    cur = mysql.connection.cursor()
    cur.execute(f"select c_id as cc from _order where order_id = '{oid}'")
    res = cur.fetchall()
    cid = res[0]['cc']
    cur.execute(f"select count(*) as ex from billing_info where order_id = {oid}")
    result1 = cur.fetchall()
    if result1[0]['ex'] == 0:
        bill_num = random.randint(1000000,9999999)
        tracking_num = random.randint(1000000,9999999)
        courier = random.randint(1000000,9999999)
        cur.execute(f"insert into billing_info (bill_no, order_id, gst) values ('{bill_num}', '{oid}', '0')")
        cur.connection.commit()
        cur.execute(f"insert into shipping values ('{oid}', '{tracking_num}', '{courier}', '2022-06-21', 'Soon')")
        cur.connection.commit()
    else:
        cur.execute(f"select * from billing_info where order_id = '{oid}'")
        result2 = cur.fetchall()
        bill_num = result2[0]['bill_no']
        cur.execute(f"select * from shipping where order_id = '{oid}'")
        result3 = cur.fetchall()
        tracking_num = result3[0]['tracking_no']
        courier = result3[0]['courier']
    cur.close()
    return render_template('checkout.html', bill_num = bill_num, order_id = oid, tracking_no = tracking_num, courier = courier, cid = cid)


@app.route("/seller/<sid>", methods=['GET', 'POST'])
def seller(sid):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        if request.form['aud'] == 'add':
            
            product_name = request.form['Product_name']
            product_category = request.form['Product_category']
            product_price = request.form['Product_price']
            product_discount = request.form['Product_discount']
            product_image = request.form['Product_image']
            product_desc = request.form['Product_desc']
            cur.execute(f"insert into product (discount, category, s_id, price, images, _desc, p_name) values ('{product_discount}', '{product_category}', '{sid}', '{product_price}', '{product_image}', '{product_desc}', '{product_name}')")
            
        elif request.form['aud'] == 'updateProduct':
            local_product_id = request.form['Product_id']
            product_name = request.form['Product_name']
            product_category = request.form['Product_category']
            product_price = request.form['Product_price']
            product_discount = request.form['Product_discount']
            product_image = request.form['Product_image']
            product_desc = request.form['Product_desc']
            cur.execute(f"update product set p_name = '{product_name}', category='{product_category}', price = '{product_price}', discount='{product_discount}', images = '{product_image}', _desc = '{product_desc}' where p_id='{local_product_id}' and s_id = '{sid}'")
            
        elif request.form['aud'] == 'delete':
            local_product_id = request.form['Product_id']
            cur.execute(f"delete from product where p_id='{local_product_id}' and s_id='{sid}'")

        elif request.form['aud'] == 'updateSeller':
            seller_first_name = request.form['First_name']
            seller_last_name = request.form['Last_name']
            pincode = request.form['Pincode']
            ph_num = request.form['Phone_num']
            email = request.form['email']
            add_line1 = request.form['add_line1']
            add_line2 = request.form['add_line2']
            city = request.form['city']
            cur.execute(f"update personal_info set first_name = '{seller_first_name}', last_name = '{seller_last_name}', add_line1 = '{add_line1}', add_line2 = '{add_line2}', city = '{city}', pincode = '{pincode}', ph_no = '{ph_num}', email_id = '{email}' where username='{sid}'")
    cur.connection.commit()
    cur.close()
    return render_template('seller.html')    


@app.route("/history/<cid>", methods=['GET', 'POST'])
def history(cid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT history.quantity,history.c_id, history.order_date ,history.p_id,history.order_id,history._status,product.p_name ,product.price ,product.category ,product.images,product.s_id,product._desc FROM history INNER JOIN product ON history.p_id=product.p_id;")
    orders = cur.fetchall()
    fresults=[]
    for i in range(len(orders)):
        if(orders[i]['c_id']==cid):
            fresults.append(orders[i])

    for i in fresults:
        i['price'] = "{:.2f}".format(i['price']*i['quantity'])
    return render_template('history.html',history = fresults, cid = cid) 
    
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    cur = mysql.connection.cursor()
    res = ''
    if request.method == "POST":
        cur.execute(request.form['query'])
        res = cur.fetchall()
        cur.close()
    return render_template('admin.html', result = res)

if __name__ == "__main__":
    app.run(debug=True)