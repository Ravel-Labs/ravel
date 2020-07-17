from api import create_app
import os

print(f'starting up Ravel API')
app = create_app()
port = os.getenv('PORT') or 5000
app.run(host='0.0.0.0', port=port, debug=False)
print(f'ravel api started on port {port}')