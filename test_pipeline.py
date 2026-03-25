from db import insert_product, insert_price

product_id = insert_product(
    "iPhone 15",
    "Apple",
    "Mobiles",
    "image_url_here"
)

if product_id:
    product_id = product_id[0]

    insert_price(
        product_id,
        "amazon",
        79999,
        "amazon_link_here"
    )

print("PIPELINE WORKED ")
