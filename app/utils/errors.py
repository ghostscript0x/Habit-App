import logging
from flask import render_template, jsonify, request

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f'Bad request: {error}')
        if request.headers.get('HX-Request'):
            return render_template('errors/400.html'), 400
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(404)
    def not_found(error):
        logger.info(f'Not found: {error}')
        if request.headers.get('HX-Request'):
            return render_template('errors/404.html'), 404
        return render_template('errors/404.html', error=error), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {error}')
        from app import db
        db.session.rollback()
        if request.headers.get('HX-Request'):
            return render_template('errors/500.html'), 500
        return render_template('errors/500.html', error=error), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f'Forbidden access: {error}')
        return render_template('errors/403.html', error=error), 403
    
    @app.errorhandler(422)
    def unprocessable(error):
        logger.warning(f'Unprocessable entity: {error}')
        return render_template('errors/422.html', error=error), 422


def handle_csrf_error(reason):
    logger.warning(f'CSRF error: {reason}')
    return jsonify({'error': 'CSRF token validation failed'}), 400
