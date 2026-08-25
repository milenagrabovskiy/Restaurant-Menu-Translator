from flask import jsonify

from menu_translator.models.restaurant import Restaurant


def single_envelope(restaurant: Restaurant):
    return jsonify(restaurant.model_dump(mode="json"))