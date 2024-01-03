from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
# para criar um db rapidamente, com dados falsos aleatórios:
from faker import Faker
import random
fake = Faker('pt_BR')
# ^^^^
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# db.init_app(app)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    # Abaixo, afirmamos uma relação entre os objetos instanciados pelas classes. Um Customer pode ter \
    # vários Orders, mas um Order pode ter apenas um Customer.
    orders = db.relationship('Order', backref='customer')

# ... por outro lado, um Order pode ter vários Product e, DA MESMA FORMA, um Product pode estar em vários Order. \
# Ou seja, a relação é de igual para igual. Sendo assim, devemos criar um ASSOCIATION TABLE:
# Suponha que eu tenha um Order e nesta Order, foram comprados os produtos com id 1, 2, e 3. Então, abaixo devemos \ 
# ASSOCIAR a Order com estes três produtos; daí ASSOCIATION TABLE:
order_product = db.Table('order_product', 
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)                         
)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    shipped_date = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    coupon_code = db.Column(db.String(50))
    # Criando a association table (abaixo). Repare que por padrão, o nome da tabela (customer, no caso) equivale ao nome da classe em minúsculas.
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    # Depois de ter criado o ASSOCIATION TABLE (acima), devemos criar a relação para produtos:
    products = db.relationship('Product', secondary=order_product)

    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)

    # PARA CRIAR MANUALMENTE UM DB.
    # APÓS TUDO ISSO, NO TERMINAL PRECISO FAZER UM SHELL PARA O FLASK, PARA IMPORTAR O DB E TAMBÉM CRIAR TODAS AS TABELAS:
    # export FLASK_APP=/caminho/para/seu/app.py

    # OBS: Sempre que eu entrar no shell do Flask eu adiciono, altero ou faço query de itens. No shell do sqlite3 eu analiso modelos do db.

    # flask shell
    # from main import db
    # db.create_all()
    # ^ Acima, criaremos de fato o banco de dados, agora na pasta 'instance'.
    # exit()   => para sair do shell do Flask.
    # sqlite3 db.sqlite3     => usar o COMANDO sqlite3 para ABRIR o db. Isto me levará para mais um shell específico, 
    # dentro do db.
    # .tables    => Me mostra os nomes das tabelas criados dentro do db.
    # .schema   => Me mostra mais detalhes sobre os campos das tabelas do db.

    # Agora, podemos inserir dados dentro do db.
    # Para isso, devemos entrar no shell do FLask:
    # flask shell
    # Agora, devemos importar objetos e classes:
    # from main import db, Product, Order, Customer
    # Inserir dados:
    # johndoe = Customer(first_name='John', last_name='Doe', address='Rua Dificil Pacas, n.12', city='Eternidade', postcode='0123456', email='vamoquevamo@dificil.com')
    # johndoe      => após clicar enter, podemos verificar que um objeto (johndoe) foi instanciado e está na memória.
    # db.session.add(johndoe)   => Adiciona johndoe para o db, mas ainda precisa commitar:
    # db.session.commit()      =>  Agora sim, está adicionado e commitado ao db.
    # exit()    => sai do shell do Flask

    # sqlite3 db.sqlite3 
    # select * from customer;     => Esta é uma query, ou seja, uma consulta. Listará todos os customers.
    
    # Vamos criar agora dois product:
    # flask shell
    # from main import db, Customer, Order, Product
    # computer = Product(name='Acer', price=1250)
    # db.session.add(computer)
    # db.commit()
    # phone = Product(name='LG phone', price=1250)
    # db.session.add(phone)
    # db.commit()

    #Vamos criar agora um Order no Flask Shell:
    # new_order = Order(coupon_name='FREESHIPPING', customer_id=1, products=[computer, phone])

    # sqlite3 db.sqlite3 
    # select * from order_product;     => Esta é uma query, ou seja, uma consulta. Listará a tabela em que há relação entre order (lado esquerdo) e product(lado direito).

    # EDITANDO uma entrada (um customer, por exemplo) no flask shell:
    # from main import db, Customer
    # johndoe = Customer.query.filter_by(id=1).first()
    # Se eu digitar:
    # johndoe.address
    # Retornará o endereço cadastrado originalmente. Para alterar, basta declarar diretamente:
    # johndoe.address = "Rua Nova, n.12"
    # db.session.commit()

    # DELETANDO uma entrada (um customer, por exemplo) no flask shell, fazemos a mesma coisa do add(), mas ao invés, usamos delete().
    # from main import db, Customer
    # johndoe = Customer.query.filter_by(first_name='john').first()
    # Se eu digitar, apenas para testar:
    # johndoe.address
    # Retornará o endereço cadastrado originalmente. 
    # Para deletar a entrada, basta:
    # db.session.delete(johndoe)
    # db.session.commit()

# Para criar um db cheio de dados falsos e aleatórios:
    
def add_customers():
    for n in range(100):
        customer = Customer(
            first_name = fake.first_name(),
            last_name = fake.last_name(),
            address = fake.street_address(),
            city = fake.city(),
            postcode = fake.postcode(),
            email=fake.email()
        )
        db.session.add(customer)
    db.session.commit()

def add_orders():
    customers = Customer.query.all()

    for n in range(1000):
        #escolher um cliente aleatório:
        customer = random.choice(customers)
        
        order_date = fake.date_time_this_year()
        shipped_date = random.choices([None, fake.date_time_between(start_date=order_date)], [10,90])[0]
        delivered_date = None
        if shipped_date:
            delivered_date = random.choices([None, fake.date_time_between(start_date=shipped_date)], [50,50])[0]

        coupon_code = random.choices([None, '50OFF', 'FREESHIPPING', 'BUYONEGETTWO'], [80, 5, 5, 5])[0]

        order = Order(
            customer_id=customer.id, 
            order_date=order_date,
            shipped_date=shipped_date,
            delivered_date=delivered_date,
            coupon_code=coupon_code
        )
        db.session.add(order)
    db.session.commit()

def add_products():
    for n in range(10):
        product = Product(
            name=fake.color_name(),
            price=random.randint(10,100)
       )
        db.session.add(product)
    db.session.commit()

def add_order_products():
    orders = Order.query.all()
    products = Product.query.all()

    for order in orders:
        k = random.randint(1, 3)
        purchased_products = random.sample(products, k)
        order.products.extend(purchased_products)
    db.session.commit()

def create_random_data():
    db.create_all()
    add_customers()
    add_orders()
    add_products()
    add_order_products()

def get_orders_by(customer_id=1):
    customer_orders = Order.query.filter_by(customer_id=customer_id).all()
    for order in customer_orders:
        print(f"Order ID: {order.id}\nCustomer First Name: {order.customer.first_name}\nOrder Date: {order.order_date}")

def get_pending_orders():
    pending_orders = Order.query.filter(Order.shipped_date.is_(None)).order_by(Order.order_date.desc()).all()
    for order in pending_orders:
        print(order.id)

def how_many_customers():
    print(Customer.query.count())

def orders_with_code(coupon_id=None):
    """Return order details given a coupon id (1= None, 2= '50OFF', 3= 'FREESHIPPING', 4= 'BUYONEGETTWO')"""
    coupon_options = {
        1: None,
        2: '50OFF',
        3: 'FREESHIPPING',
        4: 'BUYONEGETTWO'
    }
    owc = Order.query.filter_by(coupon_code=coupon_options[coupon_id]).order_by(Order.order_date).all()
    for order in owc:
        print(f"Order ID: {order.id}\nOrder Date: {order.order_date}\nCustomer Last Name: {order.customer.last_name}\nCoupon Code: {order.coupon_code}\n")

def revenue_by_period(num_of_days: int):
    """Return total revenue given a number of past days"""
    # Retrieving dates
    today = datetime.now()
    query_date = today - timedelta(days=num_of_days)
    
    # now, the query:
    revenue = db.session.query(db.func.sum(Product.price)).join(order_product).join(Order).filter(Order.order_date > query_date).scalar()
    print(revenue)

def average_fulfillment_time():
    print(db.session.query(
        db.func.time(
            db.func.avg(
                db.func.strftime('%s', Order.shipped_date) - db.func.strftime('%s', Order.order_date)
            ), 
            'unixepoch'
        )
    ).filter(Order.shipped_date.isnot(None)).scalar()
    )

def customers_spent_by_amount(spent_money):
    selected_customers = db.session.query(Customer, db.func.sum(Product.price).label('total_spent')).join(Order).join(order_product).join(Product).group_by(Customer).having(db.func.sum(Product.price) > spent_money).all()
    
    results = []
    for customer, total_spent in selected_customers:
        results.append({
            'Customer Name: ': customer.first_name,
            'Total Spent': total_spent
        }
        )
    print(results)