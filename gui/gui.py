try:
    from tkinter import *
    from tkinter.messagebox import showerror, showinfo
    from tkinter.font import Font
    from tkinter.ttk import Combobox, Treeview
except ImportError:
    from tkinter import *
    from tkinter.messagebox import showerror, showinfo
    from tkinter.font import Font
    from tkinter.ttk import Combobox, Treeview

"""Подключение к базе данных"""
try:
    from database.connect.add_connect import Database
    from database.connect.config import *

    connect = Database(host=host, port=port, user=user, password=password,
                       database=database)  # Передача переменных в класс
except Exception as ex:
    """Вывод ошибки при некорректном подключении к базе данных. 
    type(ex).__name__ возвращает название, а str(ex.args) - аргументы ошибки"""
    showerror(type(ex).__name__, str(ex.args))


class Windows(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        def min_win():  # Скрывает окно
            self.withdraw()
            self.iconify()

        # self.wm_title("ООО «Спорт»")
        self.attributes("-fullscreen", True)  # Расстягивает окно на весь экран

        title_bar = Frame(self, relief=RAISED, borderwidth=1)
        title_bar.pack(side=TOP, fill=X)

        title_lbl = Label(title_bar, text="ООО «Спорт»")
        title_lbl.pack(side=LEFT, pady=2)

        close_btn = Button(title_bar, text="X", relief=FLAT, foreground="red", activeforeground="white",
                           activebackground="red", width=2, command=lambda: self.quit())
        close_btn.pack(side=RIGHT)
        min_btn = Button(title_bar, text="_", relief=FLAT, width=2, command=min_win)
        min_btn.pack(side=RIGHT)

        container = Frame(self)
        container.pack()

        self.frames = {}  # Собирает все классы
        for F in (Authorization, Shop, Cart, Managment_Orders):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(column=0, row=0, sticky="nsew")

        self.show_frame(Authorization)

    def show_frame(self, content):
        """Переключение классов между собой"""
        frame = self.frames[content]
        frame.tkraise()


class Authorization(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        def auth():
            result = connect.get_account(login=login_entry.get(), password=password_entry.get())
            if result is not None:
                Shop.id_user = result["id_user"]
                Shop.id_privilege = result["id_privilege"]
                return controller.show_frame(Shop)

            error_label["text"] = "Неверный логин или пароль!"

        def guest_auth():
            showinfo("Внимание!", "Вы вошли как гость, некоторые функции могут быть недоступны!")

            Shop.id_user = None
            Shop.id_privilege = None
            return controller.show_frame(Shop)

        default_font = Font(font="TkDefaultFont:", weight="bold")
        entry_font = Font(font="TkTextFont:", weight="italic")

        container = LabelFrame(self, text="АВТОРИЗАЦИЯ", font=default_font, padx=500, pady=310)
        container.pack()

        login_lbl = Label(container, text="ЛОГИН", font=default_font)
        login_lbl.grid(column=0, row=0)
        password_lbl = Label(container, text="ПАРОЛЬ", font=default_font)
        password_lbl.grid(column=0, row=2)

        login_entry = Entry(container, font=entry_font)
        login_entry.grid(column=0, row=1, pady=5)
        password_entry = Entry(container, font=entry_font, show="*")
        password_entry.grid(column=0, row=3)

        error_label = Label(container, font=default_font, foreground="red")
        error_label.grid(column=0, row=4)

        auth_btn = Button(container, text="ВОЙТИ", font=default_font, width=20, foreground="black",
                          activebackground="blue", activeforeground="white", command=auth)
        auth_btn.grid(column=0, row=5)

        container_guest = Frame(self)
        container_guest.pack()

        guest_lbl = Label(container_guest, text="Нет аккаунта?", font=default_font)
        guest_lbl.grid(column=0, row=0, pady=5)
        guest_btn = Button(container_guest, text="Войти как гость", font=default_font, foreground="black",
                           activebackground="blue", activeforeground="white", command=guest_auth)
        guest_btn.grid(column=0, row=1)


class Shop(Frame):
    id_user = None
    id_privilege = None

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        def create_products_table(event):
            values = connect.get_products()
            product_table.delete(*product_table.get_children())
            for value in values:
                product_table.insert("", END, values=list(value.values()))
            product_table.grid(column=1, row=1, pady=(300, 0))

        def create_manage_btn(event):
            if self.id_privilege > 1:
                return update_orders.grid(column=1, row=4, pady=(5, 0))
            else:
                return update_orders.destroy()

        def add_prodict_to_cart():
            selected_product = product_table.selection()
            if selected_product:
                product = product_table.item(selected_product)["values"]
                id_product = connect.get_product(product[0])
                discount_price = (product[3] * product[2]) / 100
                connect.add_products_to_cart(self.id_user, id_product["id_product"], count_entry.get(),
                                             (product[2] - discount_price) * float(count_entry.get()))
                Cart.products = product

        default_font = Font(font="TkDefaultFont:", weight="bold")
        entry_font = Font(font="TkTextFont:", weight="italic")

        container = Frame(self)
        container.pack()

        quit_btn = Button(container, text="Выйти из аккаунта", font=default_font, relief=FLAT,
                          command=lambda: controller.show_frame(Authorization))
        quit_btn.grid(column=0, row=0, sticky=W)

        columns = ["product_name", "count", "price", "discount"]

        product_table = Treeview(container, columns=columns, show="headings")
        product_table.heading("product_name", text="Название продукта")
        product_table.heading("count", text="Количество на складе")
        product_table.heading("price", text="Цена руб.")
        product_table.heading("discount", text="Скидка %")

        count_lbl = Label(container, text="Введите кол-во товара:", font=default_font)
        count_lbl.grid(column=0, row=2, pady=5, sticky="e")
        count_entry = Entry(container, font=entry_font)
        count_entry.grid(column=1, row=2, pady=5)

        add_product_btn = Button(container, text="ДОБАВИТЬ В КОРЗИНУ", font=default_font, foreground="black",
                                 activebackground="blue", activeforeground="white", command=add_prodict_to_cart)
        add_product_btn.grid(column=2, row=2, pady=5)

        cart_btn = Button(container, text="ПЕРЕЙТИ В КОРЗИНУ", font=default_font, foreground="black",
                          activebackground="blue", activeforeground="white",
                          command=lambda: controller.show_frame(Cart))
        cart_btn.grid(column=1, row=3, pady=5)

        update_orders = Button(container, text="РЕДАКТИРОВАТЬ ЗАКАЗЫ", font=default_font, foreground="black",
                               activebackground="blue", activeforeground="white",
                               command=lambda: controller.show_frame(Managment_Orders))

        product_table.bind("<Enter>", create_manage_btn)
        self.bind("<Enter>", create_products_table)


class Cart(Frame):
    products = None

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        def add_products(event):
            cart_table.insert("", END, values=self.products)
            print(self.products)
            cart_table.grid(column=0, row=0)

        container = Frame(self)
        container.pack()

        columns = ["product_name", "count", "price", "discount"]

        cart_table = Treeview(container, columns=columns, show="headings")
        cart_table.heading("product_name", text="Название продукта")
        cart_table.heading("count", text="Количество на складе")
        cart_table.heading("price", text="Цена руб.")
        cart_table.heading("discount", text="Скидка %")

        self.bind("<Enter>", add_products)


class Managment_Orders(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        def create_orders_table(event):
            orders_table.grid(column=0, row=1)

        combobox_font = Font(family="TkMenuFont:")

        container = Frame(self)
        container.pack()

        values = connect.get_users()
        variable = StringVar()
        select_user_cb = Combobox(container, font=combobox_font, width=10, values=values,
                                  textvariable=variable)
        select_user_cb.grid(column=0, row=0, pady=5)

        columns = ["id_user", "id_product", "count", "price"]
        orders_table = Treeview(container, columns=columns, show="headings")
        orders_table.heading("id_user", text="ID ПОЛЬЗОВАТЕЛЯ")
        orders_table.heading("id_product", text="ID ПРОДУКТА")
        orders_table.heading("count", text="КОЛ-ВО ПРОДУКТОВ")
        orders_table.heading("price", text="ЦЕНА")

        # self.bind("<Enter>", create_orders_table)
