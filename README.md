# DVO-CRM

A comprehensive Customer Relationship Management (CRM) system designed to streamline business operations and enhance customer interactions.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Customer Management**: Efficiently manage customer profiles and interactions
- **Sales Pipeline**: Track deals and opportunities through the sales process
- **Communication Tracking**: Log all customer communications in one place
- **Reporting & Analytics**: Generate insights from customer data
- **User Management**: Role-based access control and user administration
- **Dashboard**: Real-time overview of key metrics and activities

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16.0.0 or higher)
- **npm** (v7.0.0 or higher) or **yarn**
- **Git**
- **PostgreSQL** (v12.0 or higher) or your database of choice
- **Docker** (optional, for containerized deployment)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/moda30430-cmyk/DVO-CRM.git
cd DVO-CRM
```

### 2. Install Dependencies

Using npm:
```bash
npm install
```

Or using yarn:
```bash
yarn install
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory and configure the following variables:

```env
# Server Configuration
NODE_ENV=development
PORT=3000
HOST=localhost

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dvo_crm
DB_USER=postgres
DB_PASSWORD=your_password

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRATION=7d

# API Configuration
API_BASE_URL=http://localhost:3000/api

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

## Configuration

### Database Setup

1. Create a new PostgreSQL database:

```bash
createdb dvo_crm
```

2. Run database migrations:

```bash
npm run migrate
```

3. Seed the database (optional):

```bash
npm run seed
```

### Authentication Setup

Configure your authentication provider (OAuth, SAML, or local authentication):

```bash
# Generate JWT secrets
npm run generate-keys
```

## Deployment

### Option 1: Traditional Deployment (Node.js)

#### Development Environment

```bash
npm run dev
```

The application will start on `http://localhost:3000`

#### Production Environment

```bash
# Build the application
npm run build

# Start the production server
npm start
```

### Option 2: Docker Deployment

#### Build Docker Image

```bash
docker build -t dvo-crm:latest .
```

#### Run Container

```bash
docker run -d \
  --name dvo-crm \
  -p 3000:3000 \
  --env-file .env \
  dvo-crm:latest
```

#### Using Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Option 3: Cloud Deployment (AWS, Heroku, Vercel, etc.)

#### Heroku Deployment

```bash
# Install Heroku CLI
heroku create dvo-crm

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set JWT_SECRET=your_secret

# Deploy
git push heroku main
```

#### AWS Deployment

```bash
# Using AWS Elastic Beanstalk
eb create dvo-crm-env
eb deploy
```

## Usage

### Starting the Application

```bash
npm run dev
```

### Accessing the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:3000/api
- **API Documentation**: http://localhost:3000/api/docs

### Common Tasks

#### Creating a New User

```bash
npm run create-user -- --email user@example.com --name "John Doe" --role admin
```

#### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

#### Database Operations

```bash
# Run migrations
npm run migrate

# Revert migrations
npm run migrate:revert

# Reset database
npm run db:reset
```

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh token

#### Customers
- `GET /api/customers` - List all customers
- `GET /api/customers/:id` - Get customer details
- `POST /api/customers` - Create new customer
- `PUT /api/customers/:id` - Update customer
- `DELETE /api/customers/:id` - Delete customer

#### Sales
- `GET /api/opportunities` - List opportunities
- `POST /api/opportunities` - Create opportunity
- `PUT /api/opportunities/:id` - Update opportunity

#### Reports
- `GET /api/reports/dashboard` - Dashboard metrics
- `GET /api/reports/sales` - Sales reports
- `GET /api/reports/customer` - Customer analytics

## API Documentation

For detailed API documentation, refer to the [API Documentation](./docs/API.md) file or access the interactive Swagger UI at:

```
http://localhost:3000/api/docs
```

## Troubleshooting

### Common Issues

**Port 3000 is already in use:**
```bash
# Change the PORT variable in .env
PORT=3001
```

**Database connection failed:**
```bash
# Verify PostgreSQL is running
sudo service postgresql status

# Check database credentials in .env
```

**JWT authentication errors:**
```bash
# Regenerate JWT keys
npm run generate-keys

# Update JWT_SECRET in .env
```

**Module not found errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Development

### Project Structure

```
DVO-CRM/
├── src/
│   ├── controllers/       # Request handlers
│   ├── models/            # Data models
│   ├── routes/            # API routes
│   ├── middleware/        # Custom middleware
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── index.js           # Application entry point
├── tests/                 # Test files
├── migrations/            # Database migrations
├── docs/                  # Documentation
├── .env.example           # Example environment variables
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker configuration
├── package.json           # Project dependencies
└── README.md              # This file
```

### Scripts

```json
{
  "dev": "nodemon src/index.js",
  "start": "node src/index.js",
  "build": "webpack --mode production",
  "test": "jest",
  "test:watch": "jest --watch",
  "test:coverage": "jest --coverage",
  "migrate": "node scripts/migrate.js",
  "seed": "node scripts/seed.js",
  "lint": "eslint src/",
  "format": "prettier --write src/"
}
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:

- Create an issue on GitHub
- Contact the development team
- Check existing documentation in the `/docs` folder

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.

---

**Last Updated**: January 4, 2026

For more information, visit the [project repository](https://github.com/moda30430-cmyk/DVO-CRM)
