"""Stock Management System - CMPE341 course project (Flask + PostgreSQL)."""
import os
from functools import wraps

import psycopg2
import psycopg2.extras
from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://stock:stock123@localhost:5432/stockdb")


# ---------------------------------------------------------------- database
def get_db():
    """One database connection per request."""
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL)
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=(), one=False):
    """Run a SELECT and return the rows as dictionaries."""
    with get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=()):
    """Run an INSERT / UPDATE / DELETE and commit it."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(sql, params)
        db.commit()
    except Exception:
        db.rollback()
        raise


# ------------------------------------------- authentication / authorization
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = query("SELECT * FROM app_user WHERE username = %s",
                     (request.form["username"].strip(),), one=True)
        if user and check_password_hash(user["password_hash"],
                                        request.form["password"]):
            session.clear()
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Wrong username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------- dashboard
STOCK_SQL = """
    SELECT p.product_id, p.name, c.name AS category, p.unit_price, p.min_stock,
           COALESCE(SUM(CASE WHEN m.movement_type = 'IN' THEN m.quantity
                             ELSE -m.quantity END), 0) AS stock
    FROM product p
    JOIN category c ON c.category_id = p.category_id
    LEFT JOIN stock_movement m ON m.product_id = p.product_id
    GROUP BY p.product_id, p.name, c.name, p.unit_price, p.min_stock
    ORDER BY p.name
"""


@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", rows=query(STOCK_SQL))


# ------------------------------------------------- simple tables (CRUD)
# Every table below is listed by all users, but only an admin can insert,
# update or delete its rows. A field is (column, label, type, required).
TABLES = {
    "categories": {
        "table": "category", "pk": "category_id",
        "title": "Categories", "singular": "Category",
        "list_sql": "SELECT category_id AS id, name, description "
                    "FROM category ORDER BY name",
        "columns": [("name", "Name"), ("description", "Description")],
        "fields": [("name", "Name", "text", True),
                   ("description", "Description", "text", False)],
    },
    "suppliers": {
        "table": "supplier", "pk": "supplier_id",
        "title": "Suppliers", "singular": "Supplier",
        "list_sql": "SELECT supplier_id AS id, name, phone, email, city "
                    "FROM supplier ORDER BY name",
        "columns": [("name", "Name"), ("phone", "Phone"),
                    ("email", "E-mail"), ("city", "City")],
        "fields": [("name", "Name", "text", True),
                   ("phone", "Phone", "text", False),
                   ("email", "E-mail", "email", False),
                   ("city", "City", "text", False)],
    },
    "warehouses": {
        "table": "warehouse", "pk": "warehouse_id",
        "title": "Warehouses", "singular": "Warehouse",
        "list_sql": "SELECT warehouse_id AS id, name, location "
                    "FROM warehouse ORDER BY name",
        "columns": [("name", "Name"), ("location", "Location")],
        "fields": [("name", "Name", "text", True),
                   ("location", "Location", "text", False)],
    },
    "products": {
        "table": "product", "pk": "product_id",
        "title": "Products", "singular": "Product",
        "list_sql": "SELECT p.product_id AS id, p.name, c.name AS category, "
                    "s.name AS supplier, p.unit_price, p.min_stock "
                    "FROM product p "
                    "JOIN category c ON c.category_id = p.category_id "
                    "LEFT JOIN supplier s ON s.supplier_id = p.supplier_id "
                    "ORDER BY p.name",
        "columns": [("name", "Name"), ("category", "Category"),
                    ("supplier", "Supplier"), ("unit_price", "Unit price"),
                    ("min_stock", "Min. stock")],
        "fields": [("name", "Name", "text", True),
                   ("category_id", "Category", "select", True),
                   ("supplier_id", "Supplier", "select", False),
                   ("unit_price", "Unit price", "number", True),
                   ("min_stock", "Minimum stock", "integer", True)],
        "options": {
            "category_id": "SELECT category_id AS id, name FROM category "
                           "ORDER BY name",
            "supplier_id": "SELECT supplier_id AS id, name FROM supplier "
                           "ORDER BY name",
        },
    },
}


def get_table(key):
    if key not in TABLES:
        abort(404)
    return TABLES[key]


def form_values(cfg):
    """Read the form fields of a table; empty optional fields become NULL."""
    values = []
    for column, label, kind, required in cfg["fields"]:
        value = request.form.get(column, "").strip()
        values.append(value if value != "" else None)
    return values


def form_options(cfg):
    return {column: query(sql)
            for column, sql in cfg.get("options", {}).items()}


@app.route("/<key>")
@login_required
def table_list(key):
    cfg = get_table(key)
    return render_template("list.html", key=key, cfg=cfg,
                           rows=query(cfg["list_sql"]))


@app.route("/<key>/new", methods=["GET", "POST"])
@admin_required
def table_new(key):
    cfg = get_table(key)
    if request.method == "POST":
        columns = [f[0] for f in cfg["fields"]]
        sql = "INSERT INTO {} ({}) VALUES ({})".format(
            cfg["table"], ", ".join(columns), ", ".join(["%s"] * len(columns)))
        try:
            execute(sql, form_values(cfg))
            flash(cfg["singular"] + " added.", "success")
            return redirect(url_for("table_list", key=key))
        except psycopg2.Error as error:
            flash("Could not save: " + db_message(error), "error")
    return render_template("form.html", key=key, cfg=cfg, row=request.form,
                           options=form_options(cfg), is_new=True)


@app.route("/<key>/<int:row_id>/edit", methods=["GET", "POST"])
@admin_required
def table_edit(key, row_id):
    cfg = get_table(key)
    row = query("SELECT * FROM {} WHERE {} = %s".format(cfg["table"],
                                                        cfg["pk"]),
                (row_id,), one=True)
    if row is None:
        abort(404)
    if request.method == "POST":
        columns = [f[0] for f in cfg["fields"]]
        sql = "UPDATE {} SET {} WHERE {} = %s".format(
            cfg["table"], ", ".join(c + " = %s" for c in columns), cfg["pk"])
        try:
            execute(sql, form_values(cfg) + [row_id])
            flash(cfg["singular"] + " updated.", "success")
            return redirect(url_for("table_list", key=key))
        except psycopg2.Error as error:
            flash("Could not save: " + db_message(error), "error")
            row = request.form
    return render_template("form.html", key=key, cfg=cfg, row=row,
                           options=form_options(cfg), is_new=False)


@app.route("/<key>/<int:row_id>/delete", methods=["POST"])
@admin_required
def table_delete(key, row_id):
    cfg = get_table(key)
    try:
        execute("DELETE FROM {} WHERE {} = %s".format(cfg["table"], cfg["pk"]),
                (row_id,))
        flash(cfg["singular"] + " deleted.", "success")
    except psycopg2.Error as error:
        flash("Could not delete: " + db_message(error), "error")
    return redirect(url_for("table_list", key=key))


def db_message(error):
    """Turn a database constraint error into a short readable message."""
    if isinstance(error, psycopg2.errors.ForeignKeyViolation):
        return "this record is used by other records."
    if isinstance(error, psycopg2.errors.UniqueViolation):
        return "a record with the same value already exists."
    if isinstance(error, psycopg2.errors.NotNullViolation):
        return "a required field is empty."
    if isinstance(error, psycopg2.errors.CheckViolation):
        return "a value is out of the allowed range."
    return "invalid data."


# ---------------------------------------------------------- stock movements
@app.route("/movements")
@login_required
def movements():
    rows = query("""
        SELECT m.movement_id, m.movement_date, m.movement_type, m.quantity,
               m.note, p.name AS product, w.name AS warehouse,
               u.full_name AS recorded_by
        FROM stock_movement m
        JOIN product p ON p.product_id = m.product_id
        JOIN warehouse w ON w.warehouse_id = m.warehouse_id
        JOIN app_user u ON u.user_id = m.user_id
        ORDER BY m.movement_date DESC, m.movement_id DESC
    """)
    return render_template("movements.html", rows=rows)


@app.route("/movements/new", methods=["GET", "POST"])
@login_required
def movement_new():
    """Both roles can record a stock movement."""
    if request.method == "POST":
        form = request.form
        try:
            quantity = int(form["quantity"])
        except ValueError:
            quantity = 0
        if quantity <= 0:
            flash("Quantity must be a positive whole number.", "error")
        elif (form["movement_type"] == "OUT" and quantity >
              stock_in_warehouse(form["product_id"], form["warehouse_id"])):
            flash("Not enough stock in this warehouse.", "error")
        else:
            try:
                execute("""
                    INSERT INTO stock_movement (product_id, warehouse_id,
                        user_id, movement_type, quantity, note)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (form["product_id"], form["warehouse_id"],
                      session["user_id"], form["movement_type"], quantity,
                      form.get("note", "").strip() or None))
                flash("Stock movement recorded.", "success")
                return redirect(url_for("movements"))
            except psycopg2.Error as error:
                flash("Could not save: " + db_message(error), "error")
    return render_template(
        "movement_form.html", row=request.form,
        products=query("SELECT product_id, name FROM product ORDER BY name"),
        warehouses=query(
            "SELECT warehouse_id, name FROM warehouse ORDER BY name"))


def stock_in_warehouse(product_id, warehouse_id):
    row = query("""
        SELECT COALESCE(SUM(CASE WHEN movement_type = 'IN' THEN quantity
                                 ELSE -quantity END), 0) AS stock
        FROM stock_movement
        WHERE product_id = %s AND warehouse_id = %s
    """, (product_id, warehouse_id), one=True)
    return int(row["stock"])


@app.route("/movements/<int:movement_id>/delete", methods=["POST"])
@admin_required
def movement_delete(movement_id):
    execute("DELETE FROM stock_movement WHERE movement_id = %s",
            (movement_id,))
    flash("Stock movement deleted.", "success")
    return redirect(url_for("movements"))


# -------------------------------------------------------- users (admin only)
@app.route("/users")
@admin_required
def users():
    rows = query("SELECT user_id, username, full_name, role "
                 "FROM app_user ORDER BY username")
    return render_template("users.html", rows=rows)


@app.route("/users/new", methods=["GET", "POST"])
@admin_required
def user_new():
    if request.method == "POST":
        form = request.form
        if len(form["password"]) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            try:
                execute("""
                    INSERT INTO app_user (username, password_hash, full_name,
                                          role)
                    VALUES (%s, %s, %s, %s)
                """, (form["username"].strip(), hash_password(form["password"]),
                      form["full_name"].strip(), form["role"]))
                flash("User added.", "success")
                return redirect(url_for("users"))
            except psycopg2.Error as error:
                flash("Could not save: " + db_message(error), "error")
    return render_template("user_form.html", row=request.form, is_new=True)


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def user_edit(user_id):
    row = query("SELECT user_id, username, full_name, role FROM app_user "
                "WHERE user_id = %s", (user_id,), one=True)
    if row is None:
        abort(404)
    if request.method == "POST":
        form = request.form
        if form["password"] and len(form["password"]) < 6:
            flash("Password must be at least 6 characters.", "error")
        elif user_id == session["user_id"] and form["role"] != "admin":
            flash("You cannot remove your own admin role.", "error")
        else:
            try:
                execute("UPDATE app_user SET username = %s, full_name = %s, "
                        "role = %s WHERE user_id = %s",
                        (form["username"].strip(), form["full_name"].strip(),
                         form["role"], user_id))
                if form["password"]:
                    execute("UPDATE app_user SET password_hash = %s "
                            "WHERE user_id = %s",
                            (hash_password(form["password"]), user_id))
                flash("User updated.", "success")
                return redirect(url_for("users"))
            except psycopg2.Error as error:
                flash("Could not save: " + db_message(error), "error")
        row = form
    return render_template("user_form.html", row=row, is_new=False)


@app.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def user_delete(user_id):
    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "error")
    else:
        try:
            execute("DELETE FROM app_user WHERE user_id = %s", (user_id,))
            flash("User deleted.", "success")
        except psycopg2.Error as error:
            flash("Could not delete: " + db_message(error), "error")
    return redirect(url_for("users"))


def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
