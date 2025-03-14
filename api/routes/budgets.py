from flask import Blueprint

budgets_blueprint = Blueprint('budgets', __name__)

@budgets_blueprint.route('/budgets', methods=['GET'])
def get_budgets():
    return "Budget API is working!"