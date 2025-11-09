import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -----------------
# MySQL Connection
# -----------------
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="powerzone_gym",
    cursorclass=pymysql.cursors.DictCursor
)

# -----------------
# Home Page
# -----------------
@app.route('/')
def index():
    return render_template('index.html')


# -----------------
# Member Login
# -----------------
@app.route("/member-login", methods=["GET", "POST"])
def member_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "member" and password == "member123":
            session['member_logged_in'] = True
            session['username'] = username
            return redirect(url_for("member_dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("member_login.html")


# -----------------
# Admin Login
# -----------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "admin123":
            session.clear()
            session['admin_logged_in'] = True
            session['username'] = username
            flash("Welcome, Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("admin_login.html")


# -----------------
# Logout
# -----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# -----------------
# Member Dashboard
# -----------------
@app.route("/member-dashboard")
def member_dashboard():
    if not session.get('member_logged_in'):
        flash("Please login first.", "warning")
        return redirect(url_for("member_login"))
    return render_template("member_dashboard.html")


# -----------------
# Admin Dashboard
# -----------------
@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Please login first.", "warning")
        return redirect(url_for("admin_login"))

    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total_members FROM members")
        total_members = cursor.fetchone()['total_members']

        cursor.execute("SELECT COUNT(*) AS total_trainers FROM trainers")
        total_trainers = cursor.fetchone()['total_trainers']

        cursor.execute("SELECT COUNT(*) AS total_plans FROM plans")
        total_plans = cursor.fetchone()['total_plans']

    return render_template("admin_dashboard.html",
                           total_members=total_members,
                           total_trainers=total_trainers,
                           total_plans=total_plans)


# -----------------
# MEMBER CRUD
# -----------------
@app.route("/admin/members")
def view_members():
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
    return render_template("view_members.html", members=members)


@app.route("/admin/add-member", methods=["GET","POST"])
def add_member():
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        plan = request.form['plan']

        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO members (name,email,phone,plan) VALUES (%s,%s,%s,%s)",
                           (name,email,phone,plan))
            conn.commit()
        flash("Member added successfully!", "success")
        return redirect(url_for("view_members"))
    
    return render_template("add_member.html")


@app.route("/admin/edit-member/<int:id>", methods=["GET","POST"])
def edit_member(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    with conn.cursor() as cursor:
        if request.method == "POST":
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            plan = request.form['plan']
            cursor.execute("UPDATE members SET name=%s,email=%s,phone=%s,plan=%s WHERE id=%s",
                           (name,email,phone,plan,id))
            conn.commit()
            flash("Member updated successfully!", "success")
            return redirect(url_for("view_members"))

        cursor.execute("SELECT * FROM members WHERE id=%s", (id,))
        member = cursor.fetchone()

    return render_template("edit_member.html", member=member)


@app.route("/admin/delete-member/<int:id>")
def delete_member(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM members WHERE id=%s", (id,))
        conn.commit()
    flash("Member deleted successfully!", "success")
    return redirect(url_for("view_members"))


# -----------------
# TRAINER CRUD
# -----------------
@app.route("/admin/trainers")
def view_trainers():
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM trainers")
        trainers = cursor.fetchall()
    return render_template("view_trainers.html", trainers=trainers)


@app.route("/admin/add-trainer", methods=["GET","POST"])
def add_trainer():
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form['name']
        specialization = request.form['specialization']
        email = request.form['email']
        phone = request.form['phone']

        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO trainers (name,specialization,email,phone) VALUES (%s,%s,%s,%s)",
                           (name,specialization,email,phone))
            conn.commit()
        flash("Trainer added successfully!", "success")
        return redirect(url_for("view_trainers"))

    return render_template("add_trainer.html")


# -----------------
# PLAN CRUD
# -----------------
@app.route("/admin/plans")
def view_plans():
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM plans")
        plans = cursor.fetchall()
    return render_template("view_plans.html", plans=plans)


@app.route("/admin/add-plan", methods=["GET","POST"])
def add_plan():
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']

        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO plans (title,price,description) VALUES (%s,%s,%s)",
                           (title,price,description))
            conn.commit()
        flash("Plan added successfully!", "success")
        return redirect(url_for("view_plans"))

    return render_template("add_plan.html")
@app.route("/admin/edit-plan/<int:id>", methods=["GET","POST"])
def edit_plan(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))
    with conn.cursor() as cursor:
        if request.method == "POST":
            title = request.form['title']
            price = request.form['price']
            description = request.form['description']
            cursor.execute("UPDATE plans SET title=%s, price=%s, description=%s WHERE id=%s",
                           (title, price, description, id))
            conn.commit()
            flash("Plan updated successfully!", "success")
            return redirect(url_for("view_plans"))
        cursor.execute("SELECT * FROM plans WHERE id=%s", (id,))
        plan = cursor.fetchone()
    return render_template("edit_plan.html", plan=plan)

@app.route("/admin/delete-plan/<int:id>")
def delete_plan(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM plans WHERE id=%s", (id,))
        conn.commit()
    flash("Plan deleted successfully!", "success")
    return redirect(url_for("view_plans"))

@app.route("/admin/edit-trainer/<int:id>", methods=["GET", "POST"])
def edit_trainer(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    with conn.cursor() as cursor:
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            specialization = request.form["specialization"]

            cursor.execute(
                "UPDATE trainers SET name=%s, email=%s, phone=%s, specialization=%s WHERE id=%s",
                (name, email, phone, specialization, id)
            )
            conn.commit()
            flash("Trainer updated successfully!", "success")
            return redirect(url_for("view_trainers"))

        # Fetch existing trainer details
        cursor.execute("SELECT * FROM trainers WHERE id=%s", (id,))
        trainer = cursor.fetchone()

    return render_template("edit_trainer.html", trainer=trainer)
@app.route("/admin/delete-trainer/<int:id>")
def delete_trainer(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM trainers WHERE id=%s", (id,))
        conn.commit()
    flash("Trainer deleted successfully!", "success")
    return redirect(url_for("view_trainers"))
@app.route("/plan/<string:plan_name>")
def plan_detail(plan_name):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM plans WHERE LOWER(title) = %s", (plan_name.lower(),))
        plan = cursor.fetchone()

    if not plan:
        flash("Plan not found!", "danger")
        return redirect(url_for("index"))

    return render_template("plan_detail.html", plan=plan)


# -----------------
# Run the app
# -----------------
if __name__ == "__main__":
    app.run(debug=True)
