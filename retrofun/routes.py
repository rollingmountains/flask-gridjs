from flask import Blueprint, render_template, request
from .models import Session
from . import queries

bp = Blueprint('routes', __name__)


# home page


@bp.route("/")
def index():
    return render_template('index.html')

# query page


@bp.route('/api/orders')
def get_orders():
    # extract api params value
    start = request.args.get('start')
    length = request.args.get('length')
    sort = request.args.get('sort')
    search = request.args.get('search')

    # construct the query with values in place
    data_query = queries.paginated_orders(search, start, length, sort)
    count_query = queries.total_orders(search)

    # connection to db and query execution
    with Session() as session:
        data_result = session.execute(data_query)
        count_result = session.scalar(count_query)

        # construct the response data
        # data result holds two set of values order rows and order's total per row
        data = [{**result[0].to_dict(), 'total': result[1]}
                for result in data_result]

        return {
            'data': data,
            'total': count_result
        }
