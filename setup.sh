#!/bin/bash

echo "Setting up Raha Fitness Application..."
echo ""

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=sqlite:///raha_fitness.db
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo ".env file created!"
fi

cd ..

# Frontend setup
echo ""
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "To start the frontend (in a new terminal):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Don't forget to seed sample data:"
echo "  cd backend"
echo "  python seed_data.py"



