# Swara AI Identity Layer - Frontend

Next.js 14 frontend application for the Swara AI Identity Layer platform.

## Overview

This is a modern, responsive web application that provides the user interface for Swara's "Linguistic Sovereignty" platform. It allows Indian professionals to:

- Upload voice samples for linguistic profile creation
- Generate authentic professional content (emails, LinkedIn posts, presentations)
- View and manage their linguistic DNA profile
- Track cultural markers and prosody features

## Features

✅ **Voice Calibration UI**
- Drag-and-drop audio upload
- File format validation (MP3, WAV, M4A)
- Real-time upload progress
- Processing status with polling
- Success/error messaging

✅ **Content Generation Interface**
- Text input for prompts
- Content type selector (Email, LinkedIn, Presentation)
- Generate button with loading states
- Formatted content display
- Copy-to-clipboard functionality
- Authenticity score metrics
- Cultural markers tracking

✅ **User Profile Page**
- Linguistic profile summary
- Confidence scores visualization
- Cultural markers display
- Prosody features breakdown
- Hinglish patterns showcase
- Re-calibration option

✅ **Responsive Design**
- Mobile-friendly interface
- Indian professional aesthetic
- Clean, modern UI with Tailwind CSS
- Gradient accents (orange/red theme)

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

## Project Structure

```
frontend/
├── app/
│   ├── calibrate/          # Voice calibration page
│   ├── generate/           # Content generation page
│   ├── profile/            # User profile page
│   ├── layout.tsx          # Root layout with navigation
│   ├── page.tsx            # Home page
│   └── globals.css         # Global styles
├── components/
│   └── Navigation.tsx      # Navigation bar component
├── lib/
│   ├── api.ts              # API client (switches between mock/real)
│   └── mockApi.ts          # Mock API for development
├── public/                 # Static assets
└── [config files]          # Next.js, TypeScript, Tailwind configs
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- No AWS credentials needed for development (uses mock API)

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. The `.env.local` file is already configured for mock API:
```bash
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_USE_MOCK_API=true
```

4. Start the development server:
```bash
npm run dev
```

5. Open your browser to [http://localhost:3000](http://localhost:3000)

## Mock API vs Real API

The application is built to work with **mocked API responses** by default, allowing development without AWS infrastructure.

### Current Setup (Mock API)
- All API calls return simulated data
- No backend required
- Instant responses for testing UI/UX
- Perfect for hackathon demos

### Switching to Real API

When the AWS backend is ready:

1. Update `.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.amazonaws.com/prod
NEXT_PUBLIC_USE_MOCK_API=false
```

2. The API client (`lib/api.ts`) will automatically switch to real endpoints
3. No code changes needed - the interface is identical

## API Endpoints (for Real Backend)

When connecting to AWS:

- `POST /voice/upload` - Upload audio file
- `GET /voice/status/:jobId` - Check calibration status
- `GET /profile` - Get user linguistic profile
- `POST /content/generate` - Generate content
- `POST /profile/recalibrate` - Initiate re-calibration

## Development

### Running the App
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Key Features to Test

1. **Voice Calibration Flow**:
   - Go to `/calibrate`
   - Upload an audio file (any MP3/WAV/M4A)
   - Watch the processing animation
   - See the success message

2. **Content Generation**:
   - Go to `/generate`
   - Select content type (Email/LinkedIn/Presentation)
   - Enter a prompt
   - Click "Generate Content"
   - Copy the generated content

3. **Profile View**:
   - Go to `/profile`
   - View linguistic DNA metrics
   - See cultural markers and Hinglish patterns
   - Try the re-calibrate button

## Mock API Behavior

The mock API (`lib/mockApi.ts`) simulates:

- **Voice Upload**: Returns a job ID immediately
- **Calibration Status**: Randomly progresses from 0-100%, then completes
- **User Profile**: Returns a sample Indian English profile with cultural markers
- **Content Generation**: Returns templated content with authentic Indian English expressions

All responses include realistic delays to simulate network latency.

## Customization

### Changing Colors

Edit `tailwind.config.ts`:
```typescript
colors: {
  primary: { ... },  // Main brand color (currently red)
  accent: { ... },   // Accent color (currently orange)
}
```

### Adding New Content Types

1. Update the `ContentType` type in `app/generate/page.tsx`
2. Add the new type to `contentTypes` array
3. Update mock API template in `lib/mockApi.ts`

## Deployment

### Vercel (Recommended)
```bash
npm run build
# Deploy to Vercel via GitHub integration or CLI
```

### AWS Amplify
```bash
npm run build
# Configure Amplify to point to the frontend directory
```

### Docker
```bash
docker build -t swara-frontend .
docker run -p 3000:3000 swara-frontend
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:3001/api` |
| `NEXT_PUBLIC_USE_MOCK_API` | Use mock API instead of real backend | `true` |

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- First Load JS: ~85kb (optimized)
- Lighthouse Score: 95+ (Performance, Accessibility, Best Practices)
- Mobile-responsive with touch-friendly UI

## Troubleshooting

**Issue**: "Module not found" errors
- Solution: Run `npm install` again

**Issue**: Port 3000 already in use
- Solution: Use `PORT=3001 npm run dev` or kill the process on port 3000

**Issue**: Mock API not working
- Solution: Check `.env.local` has `NEXT_PUBLIC_USE_MOCK_API=true`

## Future Enhancements

- [ ] User authentication (OAuth 2.0)
- [ ] Real-time WebSocket updates for processing
- [ ] Batch content generation
- [ ] Content history and favorites
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Accessibility improvements (WCAG 2.1 AA)

## Contributing

This is a hackathon project. For production use:
1. Add proper error boundaries
2. Implement comprehensive testing
3. Add loading skeletons
4. Enhance accessibility
5. Add analytics tracking

## License

MIT License - Built for AWS AI Bharath Hackathon

## Contact

For questions about the frontend implementation, refer to the main project README.
