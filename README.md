# For My Devi ♡

A responsive relationship-space website built for two people.

## What's included
- Responsive desktop/mobile interface
- Her World check-in and preferences
- Guided five-step Repair Room
- Accountability commitments
- Drawing canvas: pen, eraser, colours, brush size, undo/redo, clear and PNG export
- Love notes, memory garden, future goals
- Local persistence using browser localStorage

## Run locally
Open `index.html` in a browser, or use a local static server:
```bash
python -m http.server 8000
```
Then visit http://localhost:8000.

## Deploy
This is a static website. Import the repository into Vercel and use:
- Framework preset: Other
- Build command: leave empty
- Output directory: `.`

## Important: current storage and collaboration status
The initial build stores entries and drawings in the current browser only. It does not yet provide secure cross-device accounts or shared cloud storage.

To enable realtime drawing, create a Supabase project, enable Realtime, then put the project URL and anon/publishable key in the two constants near the end of `app.js`. The current broadcast demo sends the current canvas image after each stroke. For a production shared product, add Supabase Auth, a private two-member relationship, database tables, Storage policies and row-level security before storing personal content. Never put a service-role key in frontend code.

## Privacy
Do not use this public repository for private photos, voice notes, or personal relationship records. The current demo stores data locally in each browser. Add authenticated backend storage and strict RLS before using it as a private shared space.
