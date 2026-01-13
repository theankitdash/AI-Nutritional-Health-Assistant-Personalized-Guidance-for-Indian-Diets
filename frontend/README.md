# Nutrify-Health - Next.js Frontend

This is the Next.js frontend for the AI Nutritional Health Assistant application.

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Make sure your FastAPI backend is running on `http://localhost:8000`

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

- `src/app/` - Next.js app router pages and layouts
- `src/components/` - React components
  - `layout/` - Header, Sidebar
  - `modals/` - Auth, Personal Details, Preferences, Health Conditions, Account Settings
  - `chat/` - Chat interface components
  - `ui/` - Reusable UI components
- `src/lib/` - API client, types, and utilities
- `src/contexts/` - React contexts for state management
- `src/styles/` - CSS modules and global styles

## Features

- **Authentication**: Login and registration with validation
- **Personal Details**: Manage user profile information
- **Preferences**: Set dietary and lifestyle preferences
- **Health Conditions**: Track health conditions
- **Account Settings**: Change password
- **Chat Interface**: AI-powered nutritional guidance chat

## Technology Stack

- Next.js 14 (App Router)
- TypeScript
- React Context API for state management
- CSS Modules for styling
- FastAPI backend integration

## Notes

The Preferences and Health Conditions modals have simplified implementations. You may need to add all the detailed form fields from the original HTML to match the complete functionality.

## Building for Production

```bash
npm run build
npm start
```
