from app import create_app
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

# Add a test route directly in app.py
@app.route('/direct-test')
def direct_test():
    logger.debug("Direct test route accessed")
    return {"message": "Direct test successful"}, 200

# Disable any potential security middleware
app.config['WTF_CSRF_ENABLED'] = False
app.config['LOGIN_DISABLED'] = True

# Create an application context for testing
with app.app_context():
    # Initialize any context-dependent resources here if needed
    pass

if __name__ == '__main__':
    logger.info("Starting Flask application on http://127.0.0.1:7777")
    app.run(host='0.0.0.0', port=7777, debug=True)