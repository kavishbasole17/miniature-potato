import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Download, RefreshCw, Briefcase, MapPin, Calendar, Activity, DollarSign, ArrowUpRight, ChevronDown, X, Zap, Globe2, Check, Layers, TrendingUp, Award } from 'lucide-react'
import { Link } from 'react-router-dom'
import { fetchOpportunities, fetchFilterOptions, triggerScrape, exportCsvUrl } from './api'

// ── helpers ──────────────────────────────────────────────
const typeClass = (t: string) => {
  const v = t.toLowerCase()
  if (v.includes('accelerator')) return { badge: 'badge-purple', card: 'type-accelerator' }
  if (v.includes('grant'))       return { badge: 'badge-emerald', card: 'type-grant' }
  if (v.includes('conference'))  return { badge: 'badge-orange',  card: 'type-conference' }
  if (v.includes('job') || v.includes('opportunity')) return { badge: 'badge-blue', card: 'type-job' }
  return { badge: 'badge-gray', card: 'type-other' }
}

const typeIcon = (t: string) => {
  const v = t.toLowerCase()
  if (v.includes('accelerator')) return <TrendingUp className="w-3 h-3" />
  if (v.includes('grant'))       return <Award className="w-3 h-3" />
  if (v.includes('conference'))  return <Globe2 className="w-3 h-3" />
  if (v.includes('job'))         return <Briefcase className="w-3 h-3" />
  return null
}

// ── Dropdown (fixed-position to escape all stacking contexts) ────
function Dropdown({ label, icon, value, options, onChange }: {
  label: string; icon: React.ReactNode; value: string
  options: string[]; onChange: (v: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState({ top: 0, left: 0 })
  const triggerRef = useRef<HTMLButtonElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)

  // Close on outside click
  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (
        !triggerRef.current?.contains(e.target as Node) &&
        !panelRef.current?.contains(e.target as Node)
      ) setOpen(false)
    }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  // Recompute position on scroll/resize
  useEffect(() => {
    if (!open) return
    const update = () => {
      if (!triggerRef.current) return
      const r = triggerRef.current.getBoundingClientRect()
      setPos({ top: r.bottom + 6, left: r.left })
    }
    update()
    window.addEventListener('scroll', update, true)
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', update, true)
      window.removeEventListener('resize', update)
    }
  }, [open])

  const handleOpen = () => {
    if (!triggerRef.current) return
    const r = triggerRef.current.getBoundingClientRect()
    setPos({ top: r.bottom + 6, left: r.left })
    setOpen(o => !o)
  }

  const isActive = !!value

  return (
    <div>
      <button
        ref={triggerRef}
        onClick={handleOpen}
        className={`dropdown-trigger ${isActive ? 'active' : ''}`}
      >
        <span style={{ opacity: 0.5 }}>{icon}</span>
        <span>{value || label}</span>
        {isActive
          ? <X className="w-3 h-3" onClick={e => { e.stopPropagation(); onChange(''); setOpen(false) }} />
          : <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`} />
        }
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            ref={panelRef}
            className="dropdown-panel"
            style={{ top: pos.top, left: pos.left }}
            initial={{ opacity: 0, y: 6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.97 }}
            transition={{ duration: 0.13, ease: 'easeOut' }}
          >
            <div className="dropdown-list">
              <button className={`dropdown-item ${!value ? 'selected' : ''}`} onClick={() => { onChange(''); setOpen(false) }}>
                All {label}
                {!value && <Check className="w-3.5 h-3.5 check" />}
              </button>
              {options.map(o => (
                <button key={o} className={`dropdown-item ${value === o ? 'selected' : ''}`} onClick={() => { onChange(o); setOpen(false) }}>
                  <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>{o}</span>
                  {value === o && <Check className="w-3.5 h-3.5 check" />}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="opp-card type-other" style={{ minHeight: 280 }}>
      <div className="opp-card-body" style={{ gap: 14 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div className="shimmer" style={{ height: 22, width: 90, borderRadius: 99 }} />
          <div className="shimmer" style={{ height: 32, width: 32, borderRadius: 9 }} />
        </div>
        <div className="shimmer" style={{ height: 20, width: '80%' }} />
        <div className="shimmer" style={{ height: 15, width: '50%' }} />
        <div style={{ marginTop: 'auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div className="shimmer" style={{ height: 40 }} />
          <div className="shimmer" style={{ height: 40 }} />
        </div>
      </div>
    </div>
  )
}

// ── Toast ─────────────────────────────────────────────────
function Toast({ msg, type }: { msg: string; type: 'success' | 'error' | 'info' }) {
  return (
    <motion.div className={`toast ${type}`}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10 }}
    >
      {type === 'success' ? <Check className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
      {msg}
    </motion.div>
  )
}

// ── Meta row item ─────────────────────────────────────────
function Meta({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-3)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{label}</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: 'var(--text-2)', fontSize: 12, fontWeight: 500 }}>
        <span style={{ color: 'var(--text-3)', flexShrink: 0 }}>{icon}</span>
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{value}</span>
      </div>
    </div>
  )
}

// ── Dashboard ───────────────────────────────────────────────────
export default function Dashboard() {
  const [opps, setOpps] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [toast, setToast] = useState<{ msg: string; type: 'success'|'error'|'info' } | null>(null)

  const [search, setSearch] = useState('')
  const [typeF, setTypeF] = useState('')
  const [srcF, setSrcF] = useState('')
  const [stageF, setStageF] = useState('')
  const [opts, setOpts] = useState<{ types: string[]; sources: string[]; startup_stages: string[] }>({ types: [], sources: [], startup_stages: [] })

  const limit = 12
  const totalPages = Math.ceil(total / limit)
  const activeFilters = [typeF, srcF, stageF].filter(Boolean).length

  const showToast = (msg: string, type: 'success'|'error'|'info' = 'info') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 4000)
  }

  const loadData = useCallback(async (pg = page) => {
    setLoading(true)
    try {
      const d = await fetchOpportunities({ skip: (pg - 1) * limit, limit, search: search || undefined, type: typeF || undefined, source: srcF || undefined, startup_stage: stageF || undefined })
      setOpps(d.items); setTotal(d.total)
    } catch { showToast('Failed to load data', 'error') }
    setLoading(false)
  }, [page, search, typeF, srcF, stageF])

  useEffect(() => { fetchFilterOptions().then(d => setOpts(d)).catch(() => {}) }, [])
  useEffect(() => { setPage(1) }, [search, typeF, srcF, stageF])
  useEffect(() => { loadData(page) }, [page, search, typeF, srcF, stageF])

  const handleSync = async () => {
    setSyncing(true)
    try {
      const r = await triggerScrape()
      showToast(r?.message || 'Sync complete!', 'success')
      await loadData(1); await fetchFilterOptions().then(d => setOpts(d))
    } catch { showToast('Sync failed', 'error') }
    setSyncing(false)
  }

  const clearAll = () => { setSearch(''); setTypeF(''); setSrcF(''); setStageF('') }

  const TYPE_PILLS = ['Accelerator', 'Grant', 'Conference', 'Job / Opportunity']

  return (
    <div style={{ minHeight: '100vh', paddingBottom: 80 }}>

      {/* ── HEADER NAVBAR ── */}
      <header className="site-header">
        <div style={{ maxWidth: 1400, margin: '0 auto', padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>
          {/* Brand */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 32, height: 32, borderRadius: 10, background: 'linear-gradient(135deg,#4f46e5,#7c3aed)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 8px rgba(79,70,229,0.3)' }}>
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div className="logo-text" style={{ fontSize: 18, fontWeight: 800, letterSpacing: '-0.02em' }}>Startup Orbit</div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Link to="/admin/login" className="btn-ghost" style={{ textDecoration: 'none' }}>Admin Login</Link>
            <button onClick={handleSync} disabled={syncing} className={`btn-ghost ${syncing ? 'glow-ring' : ''}`}>
              <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} style={{ color: syncing ? 'var(--indigo)' : 'var(--text-2)' }} />
              {syncing ? 'Syncing…' : 'Sync Data'}
            </button>
            <a href={exportCsvUrl} className="btn-primary">
              <Download className="w-4 h-4" /> Export CSV
            </a>
          </div>
        </div>
      </header>

      {/* ── HERO SECTION ── */}
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '60px 32px 40px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
        <h1 style={{ fontSize: 48, fontWeight: 900, color: 'var(--text-1)', letterSpacing: '-0.03em', lineHeight: 1.1, marginBottom: 16 }}>
          Discover your next <span className="logo-text">Big Opportunity.</span>
        </h1>
        <p style={{ fontSize: 18, color: 'var(--text-2)', maxWidth: 600, margin: '0 auto 32px', lineHeight: 1.5 }}>
          The ultimate high-fidelity repository for startup grants, accelerators, conferences, and job opportunities.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16, flexWrap: 'wrap' }}>
          {[
            { icon: <Globe2 className="w-4 h-4" />, value: total, label: 'Curated Opportunities' },
            { icon: <Activity className="w-4 h-4" />, value: opts.types.length, label: 'Opportunity Types' },
          ].map((s, i) => (
            <div key={i} className="hero-stat-card">
              <div className="icon-wrap">{s.icon}</div>
              <div className="stat-text">
                <span className="val">{s.value}</span>
                <span className="lbl">{s.label}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── BODY ── */}
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '40px 32px 0' }}>

        {/* ── FILTER BAR ── */}
        <motion.div className="filter-bar" style={{ marginBottom: 16 }}
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        >
          {/* Search */}
          <div className="search-wrap">
            <Search className="w-4 h-4" style={{ color: 'var(--indigo)', flexShrink: 0 }} />
            <input
              className="search-input"
              placeholder="Search opportunities, organizers, locations…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <AnimatePresence>
              {search && (
                <motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  onClick={() => setSearch('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', display: 'flex', padding: 4 }}>
                  <X className="w-3.5 h-3.5" />
                </motion.button>
              )}
            </AnimatePresence>
          </div>

          <div className="v-divider" />

          {/* Dropdowns */}
          <div style={{ display: 'flex', alignItems: 'center', padding: '0 8px', gap: 4 }}>
            <Dropdown label="Type" icon={<Layers className="w-3.5 h-3.5" />} value={typeF} options={opts.types} onChange={setTypeF} />
            <Dropdown label="Source" icon={<Globe2 className="w-3.5 h-3.5" />} value={srcF} options={opts.sources} onChange={setSrcF} />
            <Dropdown label="Stage" icon={<TrendingUp className="w-3.5 h-3.5" />} value={stageF} options={opts.startup_stages} onChange={setStageF} />

            {activeFilters > 0 && (
              <button onClick={clearAll} style={{ marginLeft: 6, padding: '6px 10px', borderRadius: 8, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', fontSize: 12, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4, transition: 'color 0.2s' }}
                onMouseEnter={e => (e.currentTarget.style.color = '#f87171')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-3)')}>
                <X className="w-3 h-3" /> Clear
              </button>
            )}
          </div>
        </motion.div>

        {/* ── TYPE PILLS ── */}
        <motion.div className="pill-row" style={{ marginBottom: 32 }}
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        >
          <button className={`filter-pill ${!typeF ? 'active' : ''}`} onClick={() => setTypeF('')}>All</button>
          {TYPE_PILLS.map(t => (
            <button key={t} className={`filter-pill ${typeF === t ? 'active' : ''}`} onClick={() => setTypeF(typeF === t ? '' : t)}>
              {typeIcon(t)}{t}
            </button>
          ))}
          <div style={{ marginLeft: 'auto', fontSize: 13, color: 'var(--text-3)', fontWeight: 500 }}>
            <span style={{ color: 'var(--text-1)', fontWeight: 700 }}>{opps.length}</span> of <span style={{ color: 'var(--text-1)', fontWeight: 700 }}>{total}</span> shown
            {(search || activeFilters > 0) && <span style={{ marginLeft: 8, color: 'var(--indigo)', background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 6, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>Filtered</span>}
          </div>
        </motion.div>

        {/* ── GRID ── */}
        <main>
          {loading ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 20 }}>
              {Array.from({ length: 9 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : opps.length === 0 ? (
            <motion.div className="card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              style={{ padding: '80px 40px', textAlign: 'center', borderStyle: 'dashed' }}>
              <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
                <Search className="w-7 h-7" style={{ color: 'var(--indigo)' }} />
              </div>
              <h3 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-1)', marginBottom: 10 }}>No results found</h3>
              <p style={{ color: 'var(--text-3)', maxWidth: 380, margin: '0 auto 24px' }}>
                Nothing matches your current filters. Try broadening your search or clearing the filters.
              </p>
              {(search || activeFilters > 0) && (
                <button className="btn-ghost" onClick={clearAll} style={{ margin: '0 auto' }}>Clear all filters</button>
              )}
            </motion.div>
          ) : (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 20 }}>
                <AnimatePresence mode="popLayout">
                  {opps.map((opp: any, idx: number) => {
                    const tc = typeClass(opp.type)
                    return (
                      <motion.div key={opp.id}
                        className={`opp-card ${tc.card}`}
                        initial={{ opacity: 0, y: 24 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{ duration: 0.32, delay: Math.min(idx * 0.04, 0.3), ease: 'easeOut' }}
                      >
                        <div className="opp-card-body">
                          {/* Top */}
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                            <span className={`badge ${tc.badge}`}>{typeIcon(opp.type)}{opp.type}</span>
                            <a href={opp.source_link} target="_blank" rel="noreferrer" className="link-btn">
                              <ArrowUpRight className="w-3.5 h-3.5" />
                            </a>
                          </div>

                          {/* Title */}
                          <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-1)', lineHeight: 1.35, marginBottom: 8 }}>{opp.title}</h3>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-3)', fontSize: 12, fontWeight: 500, marginBottom: 20 }}>
                            <Briefcase className="w-3.5 h-3.5" style={{ flexShrink: 0 }} />
                            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{opp.organizer}</span>
                          </div>

                          {/* Meta grid */}
                          <div style={{ marginTop: 'auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px 12px' }}>
                            {opp.location && <Meta icon={<MapPin className="w-3 h-3" />} label="Location" value={opp.location} />}
                            {opp.funding_range && opp.funding_range !== 'N/A' && <Meta icon={<DollarSign className="w-3 h-3" />} label="Funding" value={opp.funding_range} />}
                            {opp.startup_stage && <Meta icon={<Activity className="w-3 h-3" />} label="Stage" value={opp.startup_stage} />}
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                              {opp.is_remote === 'Yes'    && <span className="tag-remote">Remote</span>}
                              {opp.is_remote === 'Hybrid' && <span className="tag-hybrid">Hybrid</span>}
                              {opp.is_remote === 'No'     && <span className="tag-onsite">On-site</span>}
                            </div>
                          </div>
                        </div>

                        {/* Footer */}
                        <div className="opp-card-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-3)', fontWeight: 500 }}>
                            <Calendar className="w-3.5 h-3.5" style={{ color: 'var(--indigo)' }} />
                            {opp.deadline && opp.deadline !== 'N/A' ? opp.deadline : 'Rolling Admission'}
                          </div>
                          <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-3)', letterSpacing: '0.07em', textTransform: 'uppercase' }}>{opp.source_name}</span>
                        </div>
                      </motion.div>
                    )
                  })}
                </AnimatePresence>
              </div>

              {/* ── PAGINATION ── */}
              {totalPages > 1 && (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 56, paddingTop: 32, borderTop: '1px solid var(--border)' }}>
                  <button className="btn-ghost" disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
                  <div style={{ display: 'flex', gap: 4 }}>
                    {Array.from({ length: Math.min(totalPages, 9) }, (_, i) => i + 1).map(pg => (
                      <button key={pg} className={`page-btn ${pg === page ? 'active' : ''}`} onClick={() => setPage(pg)}>{pg}</button>
                    ))}
                    {totalPages > 9 && <span style={{ color: 'var(--text-3)', alignSelf: 'center', padding: '0 4px' }}>…{totalPages}</span>}
                  </div>
                  <button className="btn-ghost" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next →</button>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* ── TOAST ── */}
      <AnimatePresence>
        {toast && <Toast msg={toast.msg} type={toast.type} />}
      </AnimatePresence>
    </div>
  )
}
