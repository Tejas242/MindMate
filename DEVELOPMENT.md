# MindMate Development Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- PostgreSQL (optional, SQLite used by default)

### Environment Setup

1. **Clone and setup the project:**
```powershell
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup  
cd ../frontend
npm install
```

2. **Configure environment variables:**
```powershell
# Copy environment template
copy .env.example .env

# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your-api-key-here
```

### Development Mode

**Option 1: Local Development**
```powershell
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Option 2: Docker Development**
```powershell
# Start with SQLite (easier for development)
docker-compose --profile dev up backend-dev

# Or start full stack with PostgreSQL
docker-compose up
```

### Access the Application
- **Frontend:** http://localhost:3000 (or 5173 for Vite dev)
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Demo Accounts
Use these accounts to test the application:

**Student Account:**
- Email: `student@demo.com`
- Password: `password123`

**Counsellor Account:**
- Email: `counsellor@demo.com`  
- Password: `password123`

**Admin Account:**
- Email: `admin@demo.com`
- Password: `password123`

## 🏗️ Architecture Overview

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── chat.py          # Chat and messaging
│   │   ├── counsellor.py    # Counsellor dashboard
│   │   └── risk.py          # Risk assessment
│   ├── core/                # Core configuration and security
│   │   ├── config.py        # Application settings
│   │   ├── database.py      # Database connection
│   │   └── security.py      # JWT authentication
│   ├── models/              # Database models
│   │   ├── user.py          # User model
│   │   └── chat.py          # Chat-related models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── ai_service.py    # OpenAI integration
│   │   ├── risk_service.py  # Risk assessment logic
│   │   └── crisis_service.py # Crisis escalation
│   └── utils/               # Utility functions
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── contexts/            # React contexts (Auth)
│   ├── pages/               # Page components
│   │   ├── LoginPage.jsx    # Authentication
│   │   ├── StudentDashboard.jsx
│   │   ├── CounsellorDashboard.jsx
│   │   └── ChatPage.jsx     # Main chat interface
│   ├── services/            # API client
│   └── App.jsx              # Main application component
```

## 🔑 Key Features Implemented

### ✅ Role-Based Authentication
- JWT-based authentication with refresh tokens
- Three user roles: Student, Counsellor, Admin
- Protected routes and role-based access control

### ✅ AI-Powered Chat System
- OpenAI GPT-3.5 integration with custom mental health prompt
- Conversation context preservation
- Safety filtering for harmful content
- Real-time messaging interface

### ✅ Dynamic Risk Assessment
- Rule-based risk scoring system
- PHQ-2/9 and GAD-7 inspired assessment criteria
- Real-time risk level calculation (low, medium, high, crisis)
- Explainable risk factors and confidence levels

### ✅ Crisis Detection & Escalation
- Automatic crisis keyword detection
- Immediate counsellor notification system
- Crisis resource display with hotline numbers
- Auto-assignment to available counsellors

### ✅ Counsellor Dashboard
- High-risk session monitoring
- Student assignment management
- Risk trend analysis
- System-wide statistics (admin only)

### ✅ Micro-Interventions Library
- CBT-style prompts and exercises
- Breathing techniques (4-7-8, Box breathing)
- Grounding techniques (5-4-3-2-1)
- Values-based interventions
- Risk-level appropriate suggestions

### ✅ Responsive UI/UX
- Clean, accessible interface design
- Mobile-responsive layout
- Real-time chat experience
- Crisis alert notifications
- Role-based navigation

## 🔧 Configuration

### Database Configuration
The application supports both SQLite (development) and PostgreSQL (production):

```python
# SQLite (default for development)
USE_SQLITE=true
SQLITE_URL=sqlite:///./mindmate.db

# PostgreSQL (production)
USE_SQLITE=false
DATABASE_URL=postgresql://mindmate:mindmate123@localhost:5432/mindmate_db
```

### AI Configuration
```python
# OpenAI Integration
OPENAI_API_KEY=your-api-key-here

# Risk Assessment Thresholds
HIGH_RISK_THRESHOLD=0.7
MEDIUM_RISK_THRESHOLD=0.4

# Crisis Keywords (customizable)
CRISIS_KEYWORDS=["suicide", "kill myself", "end it all", ...]
```

### Security Configuration
```python
# JWT Settings
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## 🧪 Testing

### Backend Testing
```powershell
cd backend
pytest app/tests/
```

### Frontend Testing
```powershell
cd frontend
npm test
```

### API Testing
Access the interactive API documentation at http://localhost:8000/docs

## 🚀 Deployment

### Docker Production Deployment
```powershell
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment
1. **Backend:** Deploy to Railway, Render, or AWS
2. **Frontend:** Deploy to Vercel, Netlify, or AWS S3
3. **Database:** Use managed PostgreSQL service

## 🔒 Security Considerations

### Authentication Security
- JWT tokens with expiration
- Refresh token rotation
- Password hashing with bcrypt
- Role-based access control

### Data Privacy
- Anonymous session tokens for chat privacy
- No personally identifiable information in logs
- Secure password storage
- CORS protection

### Crisis Safety
- Multiple crisis detection methods
- Automatic escalation procedures
- Resource hotline integration
- Counsellor notification system

## 📊 Monitoring & Analytics

### Logging
- Structured logging with appropriate levels
- Crisis event tracking
- Error monitoring and alerting
- Performance metrics

### Analytics (Future Enhancement)
- Usage patterns and trends
- Risk level distributions
- Intervention effectiveness
- Campus wellness insights

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Make changes with appropriate tests
3. Ensure all tests pass
4. Submit pull request with description

### Code Style
- Backend: Follow PEP 8 guidelines
- Frontend: Use ESLint and Prettier
- Commit messages: Use conventional commits

## 📞 Support & Resources

### Crisis Resources
- **National Suicide Prevention Lifeline:** 988
- **Crisis Text Line:** Text HOME to 741741
- **Emergency Services:** 911

### Technical Support
- Check API documentation at `/docs`
- Review application logs for errors
- Consult the troubleshooting section below

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.11+ required)
- Verify all dependencies are installed
- Check environment variables are set
- Ensure database is accessible

**Frontend build errors:**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)
- Verify environment variables

**Database connection issues:**
- For SQLite: Check file permissions
- For PostgreSQL: Verify connection string and service status
- Check firewall settings

**OpenAI API errors:**
- Verify API key is set correctly
- Check API quota and billing status
- Review API rate limits

### Performance Optimization
- Enable Redis caching for session data
- Implement database query optimization
- Use CDN for static frontend assets
- Monitor and optimize API response times

---

**MindMate** - AI-powered mental health companion for student wellness 🧠💙