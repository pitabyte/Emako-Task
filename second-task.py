import datetime
import traceback
from sqlite3 import connect
from requests import request

for target in [-2, -3]:
    try:
        line = str(target)
        response = request(
            "GET", "https://dummy.server/products/example?id=" + line
        )
        print("data downloaded from server " + str(len(response.content)))
        
        productData = response.json()
        id = productData["id"]
        stock_id = 1
        sql = connect("sqlite.db")
        cursor = sql.cursor()

        if productData["type"] != "bundle":
            print("product loaded")
            product = productData
            for supply in product["details"]["supply"]:
                for stock in supply["stock_data"]:
                    if stock["stock_id"] == 1:
                        productSupply = stock["quantity"]
                variant_id = supply["variant_id"]
                params = (str(datetime.datetime.now())[:19], str(id), str(variant_id), str(stock_id), str(productSupply))
                cursor.execute("INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES (?, ?, ?, ?, ?)",
                    (params))
                sql.commit()
            

        elif productData["type"] == "bundle":
            print("bundle loaded")
            products = []
            for product in productData["bundle_items"]:
                products.append(product)
            print("products " + str(len(products)))
            variant_id = "NULL"
            all = []
         
            for product in products:
                productSupply = 0
                for supply in product["details"]["supply"]:
                    for stock in supply["stock_data"]:
                        if stock["stock_id"] == 1:
                            supply += stock["quantity"]
                all.append(supply)
            productSupply = min(all)
            params = (str(datetime.datetime.now())[:19], str(id), str(variant_id), str(stock_id), str(productSupply))
            cursor.execute("INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES (?, ?, ?, ?, ?)",
                (params))
            sql.commit()
        print("ok")
    except Exception:
        print(traceback.format_exc())