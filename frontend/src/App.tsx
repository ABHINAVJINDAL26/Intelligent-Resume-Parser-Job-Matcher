import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  DEMO_JOB_DESCRIPTION,
  DEMO_RESUMES,
  MatchRecord,
  fetchHealth,
  runDemoMatch,
  runUploadMatch,
} from './api';

const layerCards = [
  {
    title: 'Upload Resume',
    description: 'PDF, DOCX, TXT, ZIP',
    accent: 'violet',
  },
  {
    title: 'User Dashboard',
    description: 'Skills, roles, scores',
    accent: 'teal',
  },
  {
    title: 'Job Matching Panel',
    description: 'Scores + reasons',
    accent: 'amber',
  },
  {
    title: 'Skill Gap Analyzer',
    description: 'Missing skills + courses',
    accent: 'slate',
  },
];

function App() {
  const [useDemo, setUseDemo] = useState(true);
  const [jobDescription, setJobDescription] = useState(DEMO_JOB_DESCRIPTION);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<MatchRecord[]>([]);
  const [status, setStatus] = useState<'idle' | 'ready' | 'loading' | 'error'>('idle');
  const [message, setMessage] = useState('Connect to the backend to run matching.');

  useEffect(() => {
    fetchHealth()
      .then((ok) => {
        setStatus(ok ? 'ready' : 'error');
        setMessage(ok ? 'Backend online.' : 'Backend is responding with an error.');
      })
      .catch(() => {
        setStatus('error');
        setMessage('Backend offline. Start FastAPI at http://127.0.0.1:8000.');
      });
  }, []);

  const topResult = results[0];
  const matchedSkillCount = useMemo(
    () => results.reduce((count, item) => count + item.matched_skills.length, 0),
    [results],
  );

  const runMatching = async () => {
    try {
      setStatus('loading');
      setMessage('Running match...');
      const payload = useDemo || selectedFiles.length === 0
        ? await runDemoMatch(topK)
        : await runUploadMatch(jobDescription, selectedFiles, topK);
      setResults(payload);
      setStatus('ready');
      setMessage(`Matched ${payload.length} candidates.`);
    } catch (error) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : 'Matching failed.');
    }
  };

  return (
    <div className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Resume intelligence platform</p>
          <h1>Intelligent Resume Parser & Job Matcher</h1>
          <p className="lede">
            React frontend, layered FastAPI backend, semantic ranking, and skill-gap analysis in one flow.
          </p>
        </div>
        <div className={`status status-${status}`}>
          <span className="status-dot" />
          {message}
        </div>
      </header>

      <section className="layer-grid">
        {layerCards.map((card) => (
          <motion.article
            key={card.title}
            className={`layer-card layer-${card.accent}`}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
          >
            <p>{card.title}</p>
            <strong>{card.description}</strong>
          </motion.article>
        ))}
      </section>

      <main className="content-grid">
        <section className="panel panel-form">
          <div className="panel-head">
            <div>
              <p className="panel-label">Frontend layer</p>
              <h2>Upload Resume</h2>
            </div>
            <label className="toggle">
              <input checked={useDemo} type="checkbox" onChange={(event) => setUseDemo(event.target.checked)} />
              <span>Demo mode</span>
            </label>
          </div>

          <label className="field">
            <span>Job description</span>
            <textarea value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} rows={9} />
          </label>

          <label className="field">
            <span>Resume files</span>
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.md,.zip"
              onChange={(event) => setSelectedFiles(Array.from(event.target.files || []))}
            />
          </label>

          <label className="field slider-field">
            <span>Top candidates: {topK}</span>
            <input type="range" min={1} max={10} value={topK} onChange={(event) => setTopK(Number(event.target.value))} />
          </label>

          <button className="primary-button" type="button" onClick={runMatching} disabled={status === 'loading'}>
            {status === 'loading' ? 'Matching...' : 'Run matching'}
          </button>

          <div className="hint-list">
            <p>Supported uploads: PDF, DOCX, TXT, MD, ZIP</p>
            <p>{useDemo ? `Demo resumes loaded: ${DEMO_RESUMES.length}` : `${selectedFiles.length} file(s) selected`}</p>
          </div>
        </section>

        <section className="panel panel-results">
          <div className="panel-head">
            <div>
              <p className="panel-label">Backend API layer</p>
              <h2>Job Match Panel</h2>
            </div>
            <div className="metric">
              <span>Matched skills</span>
              <strong>{matchedSkillCount}</strong>
            </div>
          </div>

          <div className="metric-grid">
            <div className="metric-card">
              <span>Processed</span>
              <strong>{results.length || (useDemo ? DEMO_RESUMES.length : selectedFiles.length)}</strong>
            </div>
            <div className="metric-card">
              <span>Top match</span>
              <strong>{topResult?.candidate_name || 'N/A'}</strong>
            </div>
            <div className="metric-card">
              <span>Best score</span>
              <strong>{topResult ? topResult.score.toFixed(2) : '0.00'}</strong>
            </div>
          </div>

          <div className="results-table">
            <div className="table-head">
              <span>Candidate</span>
              <span>Score</span>
              <span>Matched</span>
              <span>Missing</span>
            </div>
            {(results.length > 0 ? results : DEMO_RESUMES.map((item, index) => ({
              file_name: item.file_name,
              candidate_name: item.candidate_name,
              score: 0,
              semantic_score: 0,
              skill_score: 0,
              experience_score: 0,
              matched_skills: [],
              missing_skills: [],
              experience_years: null,
              method: index === 0 ? 'demo' : 'demo',
            } as MatchRecord))).map((item) => (
              <div key={item.file_name} className="table-row">
                <strong>{item.candidate_name}</strong>
                <span>{item.score.toFixed(2)}</span>
                <span>{item.matched_skills.length ? item.matched_skills.join(', ') : 'None'}</span>
                <span>{item.missing_skills.length ? item.missing_skills.slice(0, 3).join(', ') : 'None'}</span>
              </div>
            ))}
          </div>

          {topResult ? (
            <div className="insight-box">
              <p className="panel-label">Skill gap analyzer</p>
              <h3>{topResult.candidate_name}</h3>
              <p>
                Matched: {topResult.matched_skills.length ? topResult.matched_skills.join(', ') : 'None'}
              </p>
              <p>
                Missing: {topResult.missing_skills.length ? topResult.missing_skills.slice(0, 5).join(', ') : 'None'}
              </p>
            </div>
          ) : null}
        </section>
      </main>
    </div>
  );
}

export default App;
