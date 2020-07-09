from api import create_app

print(f'starting up Ravel API')
app = create_app()
app.run(host='0.0.0.0', port=5000, debug=False)
