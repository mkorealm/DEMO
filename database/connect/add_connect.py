class Database:
    def __init__(self, host, port, user, password, database):
        try:
            from pymysql import connect
            from pymysql.cursors import DictCursor
        except ImportError:
            from pymysql import connect
            from pymysql.cursors import DictCursor

        self.connect = connect(host=host,
                               port=port,
                               user=user,
                               password=password,
                               database=database,
                               cursorclass=DictCursor)

        self.cursor = self.connect.cursor()

    def get_account(self, login, password):
        sql = f"SELECT * FROM users WHERE login = '{login}' AND password = '{password}'"
        self.cursor.execute(sql)
        account = self.cursor.fetchone()
        return account

    def get_products(self):
        sql = f"SELECT product_name, count, price, discount FROM products"
        self.cursor.execute(sql)
        products = self.cursor.fetchall()
        return products

    def get_product(self, product_name):
        sql = f"SELECT id_product FROM products WHERE product_name = '{product_name}'"
        self.cursor.execute(sql)
        id_product = self.cursor.fetchone()
        return id_product

    def add_products_to_cart(self, id_user, id_product, count, price):
        sql = f"INSERT INTO cart(id_user, id_product, count, price) VALUES({id_user}, {id_product}, {count}, {price})"
        self.cursor.execute(sql)
        self.connect.commit()

    def get_users(self):
        sql = f"SELECT login FROM users"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        users = []
        for user in result:
            users.append(user["login"])
        return users
