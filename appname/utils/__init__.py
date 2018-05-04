from flask import request


def get_locale():
    rv = request.accept_languages.best_match(['zh', 'en'])
    return rv or 'en'
