import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash

from pharmacy.db import init_db
from pharmacy import db as db_module
from pharmacy import services


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-key")

# Ensure database exists
init_db()


@app.route("/")
def index():
    products = services.list_products_with_stock()
    total_stock = sum(int(p["stock_on_hand"]) for p in products)
    alerts = services.get_alerts()
    return render_template(
        "dashboard.html",
        num_products=len(products),
        total_stock=total_stock,
        low_stock=len(alerts["low_stock"]),
        near_expiry=len(alerts["near_expiry"]),
        expired=len(alerts["expired"]),
    )


@app.route("/products", methods=["GET", "POST"])
def products_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sku = request.form.get("sku") or None
        unit = request.form.get("unit") or None
        threshold = int(request.form.get("low_stock_threshold") or 0)
        if not name:
            flash("Product name is required", "error")
        else:
            try:
                services.add_product(name, sku, unit, threshold)
                flash("Product added", "success")
                return redirect(url_for("products_page"))
            except Exception as exc:
                flash(f"Error: {exc}", "error")
    products = services.list_products_with_stock()
    return render_template("products.html", products=products)


@app.route("/receive", methods=["GET", "POST"])
def receive_page():
    products = services.list_all_products()
    if request.method == "POST":
        product_id = int(request.form.get("product_id"))
        quantity = int(request.form.get("quantity"))
        expiry_date = request.form.get("expiry_date")
        supplier_name = request.form.get("supplier_name") or None
        lot_number = request.form.get("lot_number") or None
        unit_cost = request.form.get("unit_cost")
        unit_cost = float(unit_cost) if unit_cost else None
        try:
            services.receive_stock(
                product_id, quantity, expiry_date, supplier_name, lot_number, unit_cost
            )
            flash("Stock received", "success")
            return redirect(url_for("batches_page"))
        except Exception as exc:
            flash(f"Error: {exc}", "error")
    return render_template("receive.html", products=products)


@app.route("/sell", methods=["GET", "POST"])
def sell_page():
    products = services.list_all_products()
    unsatisfied = None
    if request.method == "POST":
        product_id = int(request.form.get("product_id"))
        quantity = int(request.form.get("quantity"))
        unit_price = request.form.get("unit_price")
        unit_price = float(unit_price) if unit_price else None
        try:
            sale_id, unsatisfied = services.sell_product(product_id, quantity, unit_price)
            if unsatisfied and unsatisfied > 0:
                flash(f"Partial sale. Unsatisfied quantity: {unsatisfied}", "warning")
            else:
                flash("Sale recorded", "success")
        except Exception as exc:
            flash(f"Error: {exc}", "error")
    return render_template("sell.html", products=products, unsatisfied=unsatisfied)


@app.route("/batches")
def batches_page():
    product_id = request.args.get("product_id")
    product_id_int = int(product_id) if product_id else None
    batches = services.list_batches(product_id_int)
    products = services.list_all_products()
    return render_template("batches.html", batches=batches, products=products, selected_product=product_id_int)


@app.route("/alerts")
def alerts_page():
    alerts = services.get_alerts()
    return render_template(
        "alerts.html",
        low_stock=alerts["low_stock"],
        near_expiry=alerts["near_expiry"],
        expired=alerts["expired"],
    )


@app.route("/reports/sales", methods=["GET"]) 
def sales_report_page():
    start = request.args.get("start") or date.today().replace(day=1).isoformat()
    end = request.args.get("end") or date.today().isoformat()
    rows = services.sales_report(start, end)
    total = sum((r["quantity"] or 0) * (r["unit_price"] or 0) for r in rows)
    return render_template("sales_report.html", rows=rows, start=start, end=end, total=total)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
