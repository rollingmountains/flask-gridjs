import os
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import Table, Column, create_engine, MetaData
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# create db engine and session factory

engine = None

Session = None


def init_db(app):
    global engine, Session

    db_url = app.config['DATABASE_URL']
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)

# Define base Model


class Model(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        })


ProductCountry = Table(
    'product_countries',
    Model.metadata,
    Column('product_id', sa.ForeignKey('products.id'),
           primary_key=True, nullable=False),
    Column('country_id', sa.ForeignKey('countries.id'),
           primary_key=True, nullable=False)
)


class Product(Model):
    __tablename__ = 'products'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    manufacturer_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('manufacturers.id'), index=True)
    year: so.Mapped[int] = so.mapped_column(sa.Integer, index=True)
    cpu: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))
    manufacturer: so.Mapped['Manufacturer'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='products')
    countries: so.Mapped[list['Country']] = so.relationship(
        secondary=ProductCountry, lazy='selectin', back_populates='products')
    order_items: so.WriteOnlyMapped['OrderItem'] = so.relationship(
        back_populates='product')
    reviews: so.WriteOnlyMapped['ProductReview'] = so.relationship(
        back_populates='product')
    blog_articles: so.WriteOnlyMapped['BlogArticle'] = so.relationship(
        back_populates='product')

    def __repr__(self):
        return f'Product(id: {self.id}, name: "{self.name}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'manufacturer': self.manufacturer.to_dict(),
            'year': self.year,
            'cpu': self.cpu,
            'countries': [country.to_dict() for country in self.countries],
        }


class Manufacturer(Model):
    __tablename__ = 'manufacturers'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), unique=True)
    products: so.Mapped[list['Product']] = so.relationship(
        lazy='selectin', cascade='all, delete-orphan', back_populates='manufacturer')

    def __repr__(self):
        return f'Manufacturer({self.id}, "{self.name}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Country(Model):
    __tablename__ = 'countries'

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, primary_key=True, index=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(32), unique=True, nullable=False)
    products: so.Mapped[list['Product']] = so.relationship(
        secondary=ProductCountry, lazy='selectin', back_populates='countries')

    def __repr__(self):
        return f'Country({self.id}, "{self.name}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Order(Model):
    __tablename__ = 'orders'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    customer_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('customers.id'), index=True)
    customer: so.Mapped['Customer'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='orders')
    order_items: so.Mapped[list['OrderItem']] = so.relationship(
        lazy='selectin', back_populates='order')

    def __repr__(self):
        return f'Order({self.id.hex})'

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'customer': self.customer.to_dict(),
            'order_items': [item.to_dict() for item in self.order_items]
        }


class Customer(Model):
    __tablename__ = 'customers'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(32), index=True, unique=True)
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))
    orders: so.WriteOnlyMapped['Order'] = so.relationship(
        back_populates='customer')
    reviews: so.WriteOnlyMapped['ProductReview'] = so.relationship(
        back_populates='customer')
    blog_users: so.WriteOnlyMapped['BlogUser'] = so.relationship(
        back_populates='customer')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id.hex}, {self.name})'

    def to_dict(self):
        return {
            'id': self.id.hex,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
        }


class OrderItem(Model):
    __tablename__ = 'orders_items'

    product_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('products.id'), primary_key=True, index=True)
    order_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('orders.id'), primary_key=True, index=True)
    unit_price: so.Mapped[float]
    quantity: so.Mapped[int]

    product: so.Mapped['Product'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='order_items')
    order: so.Mapped['Order'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='order_items')

    def __repr__(self):
        return f'Order_List({self.product_id, self.order_id, self.unit_price, self.quantity})'

    def to_dict(self):
        return {
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'unit_price': self.unit_price
        }


class ProductReview(Model):
    __tablename__ = 'products_reviews'

    customer_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('customers.id'), primary_key=True)
    product_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('products.id'), primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True)
    rating: so.Mapped[int] = so.mapped_column(sa.Integer)
    comment: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    product: so.Mapped['Product'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='reviews')
    customer: so.Mapped['Customer'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='reviews')

    def __repr__(self):
        return f'Review({self.customer_id.hex}, {self.product_id}, {self.rating}, {self.comment}, {self.timestamp})'


class BlogArticle(Model):
    __tablename__ = 'blog_articles'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True)
    product_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('products.id'), index=True)
    author_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('blog_authors.id'), index=True)
    language_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('languages.id'), index=True)
    translation_of_id: so.Mapped[Optional['BlogArticle']] = so.mapped_column(
        sa.ForeignKey('blog_articles.id'), index=True)

    product: so.Mapped[Optional['Product']] = so.relationship(
        lazy='joined', back_populates='blog_articles')
    author: so.Mapped['BlogAuthor'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='articles')
    views: so.WriteOnlyMapped['BlogView'] = so.relationship(
        back_populates='article')
    language: so.Mapped[Optional['Language']] = so.relationship(
        lazy='joined', back_populates='articles')
    translation_of: so.Mapped[Optional['BlogArticle']] = so.relationship(
        remote_side=id, lazy='joined', back_populates='translations')
    translations: so.Mapped[list['BlogArticle']] = so.relationship(
        lazy='selectin', back_populates='translation_of')

    def __repr__(self):
        return f"Atricle({self.id, self.title})"


class BlogAuthor(Model):
    __tablename__ = 'blog_authors'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True)
    articles: so.WriteOnlyMapped['BlogArticle'] = so.relationship(
        back_populates='author')

    def __repr__(self):
        return f"Author({self.id, self.name})"


class BlogUser(Model):
    __tablename__ = 'blog_users'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    customer_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('customers.id'), index=True)

    customer: so.Mapped[Optional['Customer']] = so.relationship(
        lazy='joined', back_populates='blog_users')
    sessions: so.WriteOnlyMapped['BlogSession'] = so.relationship(
        back_populates='user')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id.hex})'


class BlogSession(Model):
    __tablename__ = 'blog_sessions'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('blog_users.id'), index=True)

    user: so.Mapped['BlogUser'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='sessions')
    views: so.WriteOnlyMapped['BlogView'] = so.relationship(
        back_populates='session')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id.hex})'


class BlogView(Model):
    __tablename__ = 'blog_views'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    article_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('blog_articles.id'), index=True)
    session_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('blog_sessions.id'), index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True)

    article: so.Mapped['BlogArticle'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='views')
    session: so.Mapped['BlogSession'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='views')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id})'


class Language(Model):
    __tablename__ = 'languages'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32))

    articles: so.Mapped[list['BlogArticle']] = so.relationship(
        lazy='selectin', back_populates='language')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id}, {self.name})'
