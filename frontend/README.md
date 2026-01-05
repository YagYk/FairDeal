# FairDeal Frontend

A modern, beautiful React + TypeScript frontend for contract analysis.

## Features

- 🎨 **Modern Design**: Dark theme with gold accents, inspired by premium design studios
- 📊 **Interactive Charts**: Recharts-powered percentile visualizations
- 🎭 **Smooth Animations**: Framer Motion for delightful user experience
- 📱 **Responsive**: Works beautifully on all screen sizes
- ⚡ **Fast**: Built with Vite for lightning-fast development

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **Lucide React** - Icons

## Getting Started

### Install Dependencies

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── UploadSection.tsx
│   │   ├── ProgressSteps.tsx
│   │   ├── AnalysisDashboard.tsx
│   │   ├── FairnessScore.tsx
│   │   ├── PercentileCharts.tsx
│   │   ├── RedFlags.tsx
│   │   ├── FavorableTerms.tsx
│   │   └── NegotiationScripts.tsx
│   ├── types.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

## Design System

### Colors

- **Dark Background**: `#0a0a0a` to `#2a1a0a` (gradient)
- **Gold Accent**: `#D4AF37`
- **Glass Effect**: Dark with backdrop blur

### Typography

- **Sans-serif**: Inter (headings, body)
- **Serif**: Playfair Display (accent text, italic)

### Components

All components use:
- Glass morphism effects
- Smooth animations
- Hover states with glow effects
- Responsive design

## API Integration

The frontend expects the backend API at `http://localhost:8000/api`. Update the proxy in `vite.config.ts` if needed.

## Future Enhancements

- [ ] Real-time analysis progress
- [ ] Export reports as PDF
- [ ] Save analysis history
- [ ] Comparison mode (multiple contracts)
- [ ] Dark/Light theme toggle

