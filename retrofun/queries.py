import sqlalchemy as sa
from .models import Order, Customer, OrderItem, Product

# design a function with a reponse that needs 2 different set of data
# data 1: list of order rows based on the search criteria or
# total number of orders again based on search criteria, if there is no search value then all order rows with no filter
# data 2: for search value if a filter exists then count the total value on the filtered list

# first desing the queries that will be used by the route function
# function that returns the query to fetch total order count based on search criteria


def total_orders(search):
    order_count = sa.func.count(Order.id)
    if not search:
        return sa.select(order_count)

    return (sa.select(sa.func.count(sa.distinct(Order.id))).join(Order.customer).join(Order.order_items).join(OrderItem.product).where(sa.or_(Customer.name.ilike(f'%{search}%'), Product.name.ilike(f'%{search}%')))
            )

# second desing the query to send the second part of the response, rows of order details
    """The params and their values extracted form the request
    search: filter order rows based on this value
    start: starting row indicator for example get me rows starting at number 11
    length: total size of the response for that request for example get me 20 rows starting from 11 meaning it will get 20 rows in one request
    sort: send me in the order based on the value present here for example send me in descending order of total or ascending order of name +customer name or -total
    """


def paginated_orders(search, start, length, sort):
    # select all rows in the order
    total = sa.func.sum(OrderItem.quantity * OrderItem.unit_price)
    q = sa.select(Order, total).join(Customer.orders).join(
        Order.order_items).join(OrderItem.product).group_by(Order).distinct()

    # add search filter to the query
    if search:
        q = q.where(
            sa.or_(Customer.name.ilike(f'%{search}%'),
                   Product.name.ilike(f'%{search}%')))

    # add sorting mechanism to the query using order by
    if sort:
        order = []
        valid_columns = {'timestamp', 'status', 'id'}
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]

            if name == 'customer':
                column = Customer.name
            elif name == 'total':
                column = total
            elif name in valid_columns:
                column = getattr(Order, name)
            else:
                raise ValueError(f'Invalid value for sort: {name}')

            if direction == '-':
                column = column.desc()
            order.append(column)

        if not Order:
            order = [Order.timestamp.desc()]

        q = q.order_by(*order)

    # add pagination to the query based on start and length
    q.offset(start).limit(length)

    return q
