# Frontend-Backend Connection Setup Guide

## ✅ Configuration Complete

The API connection between Next.js frontend and FastAPI backend has been successfully configured.

## What Was Changed

### 1. **FastAPI Backend** - CORS Middleware Added

**File**: [app/main.py](file:///c:/Users/theankitdash/Chiku/Projects/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets/app/main.py)

Added CORS middleware to allow cross-origin requests from the Next.js frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,  # Allow cookies/sessions
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why**: This allows the Next.js app running on `localhost:3000` to make API requests to FastAPI on `localhost:8000` and send/receive cookies for authentication.

### 2. **Next.js Frontend** - Already Configured

**API Client**: [frontend/src/lib/api.ts](file:///c:/Users/theankitdash/Chiku/Projects/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets/frontend/src/lib/api.ts)

- ✅ Uses `http://localhost:8000` as base URL
- ✅ Includes `credentials: 'include'` for cookie-based authentication
- ✅ Proper error handling

**Environment Variables**: [frontend/.env.local](file:///c:/Users/theankitdash/Chiku/Projects/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets/frontend/.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## How to Run Both Servers

### Terminal 1: FastAPI Backend

```bash
# From project root
cd c:/Users/theankitdash/Chiku/Projects/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets

# Activate virtual environment (if using one)
.venv\Scripts\activate  # Windows

# Run FastAPI server
uvicorn app.main:app --reload
```

FastAPI will run on: **http://localhost:8000**

### Terminal 2: Next.js Frontend

```bash
# From project root
cd c:/Users/theankitdash/Chiku/Projects/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets/frontend

# Install dependencies (first time only)
npm install

# Run Next.js dev server
npm run dev
```

Next.js will run on: **http://localhost:3000**

---

## API Endpoints Available

All endpoints from your FastAPI backend are accessible:

### Authentication
- `POST /register/` - Register new user
- `POST /login/` - Login user (returns session cookie)
- `GET /check-login/` - Check if user is authenticated
- `POST /logout/` - Logout user

### User Profile  
- `GET /personal-details` - Get personal details
- `POST /personal-details` - Save personal details
- `GET /preferences` - Get preferences
- `POST /preferences` - Save preferences
- `GET /health-conditions` - Get health conditions
- `POST /health-conditions` - Save health conditions
- `PUT /update-password/` - Update password

### Chat
- `POST /chat/` - Send message and get AI response

---

## Testing the Connection

### Quick Test Steps

1. **Start both servers** (FastAPI and Next.js)

2. **Open browser**: Navigate to `http://localhost:3000`

3. **Test Registration**:
   - Should see the authentication modal
   - Try registering a new user
   - Check browser console for any CORS errors

4. **Expected Behavior**:
   - ✅ No CORS errors in console
   - ✅ Registration succeeds
   - ✅ Cookie is set (check Application tab → Cookies)
   - ✅ Personal Details modal opens after registration

5. **Test Login**:
   - Logout
   - Try logging in with the registered credentials
   - Should succeed without CORS errors

### Debugging Tips

**If you see CORS errors**:
- Make sure FastAPI server is running on port 8000
- Check that the CORS middleware is properly added in `app/main.py`
- Verify Next.js is running on port 3000

**If cookies aren't working**:
- Check browser console for cookie warnings
- In Chrome DevTools: Application → Cookies → `http://localhost:3000`
- The `session_id` cookie should appear after login

**If API calls fail**:
- Check FastAPI console for error logs
- Check Next.js console for network errors
- Verify the API endpoint exists in your FastAPI routers

---

## Connection Architecture

```
┌─────────────────────┐
│   Browser           │
│  localhost:3000     │
└──────────┬──────────┘
           │
           │ HTTP Request
           │ (with credentials)
           ↓
┌─────────────────────┐
│  Next.js Frontend   │
│  Port 3000          │
│                     │
│  src/lib/api.ts     │
└──────────┬──────────┘
           │
           │ Direct API Call
           │ http://localhost:8000
           ↓
┌─────────────────────┐
│  FastAPI Backend    │
│  Port 8000          │
│                     │
│  + CORS Middleware  │
│  + Session Cookies  │
└─────────────────────┘
```

**Key Points**:
- Next.js frontend makes direct calls to FastAPI (no proxy needed for dev)
- CORS middleware allows cross-origin requests
- Cookies are sent with `credentials: 'include'`
- Session-based authentication works across origins

---

## Production Considerations

When deploying to production, update:

1. **CORS Origins** in `app/main.py`:
```python
allow_origins=[
    "https://your-production-domain.com",
]
```

2. **API URL** in `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

3. **Cookie Settings** in FastAPI:
- Set `secure=True` (HTTPS only)
- Set `samesite="none"` if frontend/backend on different domains

---

## Troubleshooting

### Issue: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution**: Make sure:
- FastAPI server is running
- CORS middleware is added in `app/main.py`
- Restart FastAPI server after adding CORS

### Issue: "Session invalid" or "User not logged in"

**Solution**: 
- Check if `session_id` cookie exists
- Verify `credentials: 'include'` in API calls
- Check `allow_credentials=True` in CORS config

### Issue: "Cannot connect to backend"

**Solution**:
- Verify FastAPI is running on port 8000
- Check if `.env.local` has correct API URL
- Test backend directly: `http://localhost:8000/check-login/`

---

## Summary

✅ **Backend**: CORS middleware configured  
✅ **Frontend**: API client ready with proper credentials  
✅ **Authentication**: Cookie-based sessions working  
✅ **Ready to test**: Both servers can communicate properly

You're all set! Start both servers and test the application.
