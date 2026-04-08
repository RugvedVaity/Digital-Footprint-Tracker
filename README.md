# Digital Footprint Tracker

A comprehensive web application for discovering and analyzing online presence across multiple social media platforms and websites.

## Features

### Core Functionality
- **Username Search** - Check if a username exists across 20+ platforms
- **Risk Assessment** - Calculate risk scores based on platform presence and severity
- **Multiple Detection Methods** - Status code, content, and advanced detection strategies
- **Result Caching** - Efficient caching to avoid redundant API calls

### User Features
- **User Authentication** - Register, login, and manage accounts
- **Scan History** - Track all previous scans and search history
- **Dashboard** - View statistics and recent scans at a glance
- **Profile Management** - Manage account settings and preferences

### API Features
- **RESTful API** - Programmatic access to scanning functionality
- **Batch Checking** - Check multiple usernames in one request
- **Rate Limiting** - Built-in rate limiting to prevent abuse
- **CORS Support** - Cross-origin resource sharing enabled

### Export & Reporting
- **Multiple Formats** - Export results as PDF, CSV, or JSON
- **Batch Upload** - Upload CSV files with multiple usernames
- **Email Notifications** - Receive alerts when usernames are found on new platforms

### Development Features
- **Comprehensive Logging** - Detailed logging of all operations
- **Full Test Coverage** - 80%+ code coverage with pytest
- **Docker Support** - Containerized deployment
- **Database Flexibility** - SQLite for development, PostgreSQL for production

## Supported Platforms

The application checks for usernames on 20 platforms across multiple categories:

**Social Media:** Twitter, Instagram, TikTok, Reddit, Snapchat, Pinterest
**Professional:** LinkedIn, GitHub, Stack Overflow
**Streaming:** Twitch, YouTube
**Creator/Funding:** Medium, Patreon, Quora
**Developer:** CodePen
**Messaging:** Discord, Telegram, WeChat

Each platform is rated for risk severity (Low, Medium, High) based on doxxing/privacy concerns.

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/RugvedVaity/Digital-Footprint-Tracker.git
cd Digital\ Footprint\ Scanner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings if needed
```

5. Initialize the database:
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

6. Run the application:
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Usage

### Web Interface

1. **Basic Scan** - Enter a username and click "Scan Now" to check across all platforms
2. **Create Account** - Register for an account to save scan history
3. **View Dashboard** - See statistics and recent scans
4. **Export Results** - Download scan results in your preferred format

### API Usage

#### Check Single Username
```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe"}'
```

#### Batch Check
```bash
curl -X POST http://localhost:5000/api/check-batch \
  -H "Content-Type: application/json" \
  -d '{"usernames": ["user1", "user2", "user3"]}'
```

#### Get Search History (Authenticated)
```bash
curl http://localhost:5000/api/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database (SQLite for dev, PostgreSQL for prod)
DATABASE_URL=sqlite:///digital_footprint.db

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Rate Limiting
RATELIMIT_PER_MINUTE=10
RATELIMIT_PER_HOUR=100

# Proxy (Optional)
USE_PROXY=False
PROXY_LIST=proxy1:8080,proxy2:8080
```

### Platform Configuration

Edit `/config/sites.json` to add, remove, or modify platforms:

```json
{
  "GitHub": {
    "url": "https://github.com/{username}",
    "severity": "medium",
    "detection_type": "status_code",
    "category": "Developer",
    "icon": "github"
  }
}
```

## Running Tests

Run the full test suite:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_username_scan.py -v
```

## Docker Deployment

### Build and Run

```bash
docker-compose up -d
```

This will start:
- Flask application on port 5000
- PostgreSQL database

### Docker Configuration

Edit `docker-compose.yml` to customize:
- Port mappings
- Database credentials
- Environment variables

## Project Structure

```
Digital_Footprint_Scanner/
├── config/
│   └── sites.json              # Platform configurations
├── logs/                        # Application logs
├── static/
│   ├── style.css               # CSS styling
│   └── js/
│       └── scan.js             # Client-side JavaScript
├── templates/
│   ├── index.html              # Home page
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # User dashboard
│   ├── profile.html            # User profile
│   └── scan_detail.html        # Scan details
├── tests/                       # Test files
│   ├── test_models.py
│   ├── test_username_scan.py
│   ├── test_api.py
│   ├── test_auth.py
│   └── test_detection.py
├── app.py                      # Main Flask application
├── auth.py                     # Authentication blueprint
├── config.py                   # Configuration management
├── detection.py                # Username detection engines
├── email.py                    # Email functionality
├── logger.py                   # Logging setup
├── models.py                   # Database models
├── username_scan.py            # Scanning logic
├── .env                        # Environment variables (git-ignored)
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

## API Endpoints

### Authentication Endpoints
- `POST /auth/register` - Create new account
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - View user profile

### Scanning Endpoints
- `GET/POST /` - Home page (username scan)
- `POST /api/check` - Check single username (API)
- `POST /api/check-batch` - Check multiple usernames (API)
- `GET /api/results/<scan_id>` - Get specific scan results

### User Endpoints
- `GET /dashboard` - User dashboard with statistics
- `GET /scan/<scan_id>` - View detailed scan results
- `GET /api/history` - Get user's search history

## Security Considerations

- Passwords are hashed using werkzeug's secure hash algorithm
- CSRF protection enabled for forms
- Rate limiting prevents abuse
- User data is isolated per account
- HTTPS recommended for production
- Environment variables for sensitive data

## Limitations & Known Issues

1. **Dynamic Content** - Some platforms use JavaScript rendering; detection may fail
2. **Rate Limiting** - Rapid requests may trigger platform rate limits
3. **Changing URLs** - Platform URL structures may change; sites.json may need updates
4. **Geo-Blocking** - Some platforms may block access from certain regions

## Development Roadmap

- [ ] Real-time WebSocket updates
- [ ] Advanced analytics and trends
- [ ] Linked account detection and visualization
- [ ] Proxy rotation for better reliability
- [ ] Scheduled automated scans
- [ ] Browser extensions
- [ ] Mobile app

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Disclaimer

This tool is designed for educational and authorized security testing purposes only. Users are responsible for ensuring they have permission before scanning any usernames. Unauthorized access or misuse may violate laws.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: your-email@example.com
- Documentation: https://docs.example.com

## Changelog

### v1.0.0 (Current)
- Initial release
- 20+ platform support
- User authentication
- API endpoints
- Docker deployment
- Comprehensive testing
