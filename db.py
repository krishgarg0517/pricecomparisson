import psycopg2


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="price_tracker",
        user="postgres",
        password="postgres"   # <-- put your password if different
    )


def insert_product(title, brand, category, image_url):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO products (title, brand, category, image_url)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (title, brand)
    DO UPDATE SET title = EXCLUDED.title
    RETURNING id;
    """

    cursor.execute(query, (title, brand, category, image_url))

    product_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return product_id


def insert_price(product_id, platform, price, url):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO product_prices (product_id, platform, price, product_url)
    VALUES (%s, %s, %s, %s);
    """

    cursor.execute(query, (product_id, platform, price, url))

    conn.commit()
    cursor.close()
    conn.close()
