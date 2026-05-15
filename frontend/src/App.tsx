import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard.tsx'
import Upload from './pages/Upload.tsx'
import Review from './pages/Review.tsx'

export default function App(){
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <header className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b border-white/60">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-widest text-steel">DocPro</div>
              <div className="text-xl font-display font-semibold">Document Control</div>
            </div>
            <nav className="flex items-center gap-3 text-sm">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  isActive
                    ? 'px-3 py-2 rounded-full bg-ink text-white'
                    : 'px-3 py-2 rounded-full border border-ink/10 bg-white'
                }
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/upload"
                className={({ isActive }) =>
                  isActive
                    ? 'px-3 py-2 rounded-full bg-ink text-white'
                    : 'px-3 py-2 rounded-full border border-ink/10 bg-white'
                }
              >
                Upload
              </NavLink>
            </nav>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard/>} />
            <Route path="/upload" element={<Upload/>} />
            <Route path="/documents/:id" element={<Review/>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
