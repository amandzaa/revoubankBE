from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(debug=True)