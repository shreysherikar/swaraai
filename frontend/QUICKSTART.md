# Swara Frontend - Quick Start Guide

Get the Swara frontend running in 2 minutes!

## Prerequisites

- Node.js 18+ installed
- Terminal/Command Prompt

## Steps

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install all required packages (~2 minutes).

### 2. Start Development Server

```bash
npm run dev
```

### 3. Open in Browser

Navigate to: **http://localhost:3000**

That's it! The app is now running with mock API responses.

## What You'll See

### Home Page (/)
- Welcome message and feature overview
- Links to Calibrate, Generate, and Profile pages
- Impact statistics and "How It Works" section

### Calibrate Page (/calibrate)
- Drag-and-drop audio upload
- File validation for MP3, WAV, M4A
- Processing animation with progress bar
- Success message with next steps

### Generate Page (/generate)
- Content type selector (Email, LinkedIn, Presentation)
- Prompt input field
- Generate button
- Real-time content generation
- Copy-to-clipboard functionality
- Authenticity metrics

### Profile Page (/profile)
- Linguistic profile summary
- Confidence score visualization
- Cultural markers display
- Prosody features
- Hinglish patterns
- Re-calibrate button

## Testing the App

### Test Voice Calibration
1. Go to http://localhost:3000/calibrate
2. Upload any audio file (MP3, WAV, or M4A)
3. Click "Start Calibration"
4. Watch the progress bar (mock API will complete in ~10 seconds)
5. See success message

### Test Content Generation
1. Go to http://localhost:3000/generate
2. Select "Email" as content type
3. Enter prompt: "Announce new product launch"
4. Click "Generate Content"
5. Wait ~2 seconds for mock response
6. Copy the generated content

### Test Profile View
1. Go to http://localhost:3000/profile
2. View the mock linguistic profile
3. See cultural markers like "Actually usage", "Yaar expressions"
4. Check prosody features (speech rate, pause patterns)

## Mock API Behavior

The app uses **mock API responses** by default:

- ✅ No backend required
- ✅ Instant setup
- ✅ Realistic delays and responses
- ✅ Perfect for demos and testing

All API calls are intercepted by `lib/mockApi.ts` and return simulated data.

## Switching to Real Backend

When AWS infrastructure is ready:

1. Update `.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.amazonaws.com/prod
NEXT_PUBLIC_USE_MOCK_API=false
```

2. Restart the dev server:
```bash
npm run dev
```

No code changes needed!

## Common Issues

**Port 3000 in use?**
```bash
# Use a different port
PORT=3001 npm run dev
```

**Dependencies not installing?**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Changes not reflecting?**
```bash
# Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

## Next Steps

- Explore the UI and test all features
- Review the code in `app/` directory
- Check out `lib/mockApi.ts` to see mock responses
- Read `README.md` for detailed documentation

## Production Build

To create a production build:

```bash
npm run build
npm run start
```

The app will be optimized and ready for deployment.

## Need Help?

- Check `README.md` for detailed documentation
- Review code comments in source files
- Check browser console for errors (F12)

---

**Happy Hacking! 🚀**
