#!/bin/bash

echo "Setting up Raha Fitness Application..."
echo ""

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env if it doesn't exist (copy from .env.example or use PostgreSQL URL)
if [ ! -f .env ]; then
    echo "Creating .env file..."
    if [ -f ../.env.example ]; then
        cp ../.env.example .env
        echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
    else
        cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/raha_fitness
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF
    fi
    echo ".env file created! Edit .env and set DATABASE_URL to your PostgreSQL connection."
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



