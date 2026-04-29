export type MatchRecord = {
  file_name: string;
  candidate_name: string;
  score: number;
  semantic_score: number;
  skill_score: number;
  experience_score: number;
  matched_skills: string[];
  missing_skills: string[];
  experience_years: number | null;
  method: string;
};

export const DEMO_JOB_DESCRIPTION = `
Senior Data Scientist

We are looking for a Senior Data Scientist with 3+ years of experience.
Must have: Python, SQL, Machine Learning, Deep Learning, TensorFlow or PyTorch.
Good to have: NLP, data storytelling, Docker, FastAPI.
`.trim();

export const DEMO_RESUMES = [
  {
    file_name: 'Priya_Sharma.pdf',
    candidate_name: 'Priya Sharma',
    text: `
Priya Sharma | Delhi, India
Senior Data Scientist
Skills: Python, Machine Learning, TensorFlow, SQL, Data Visualization
Experience: 4 years as ML Engineer at Infosys
Education: B.Tech Computer Science, IIT Delhi
Summary: Built predictive models, worked on NLP pipelines and dashboards.
`.trim(),
  },
  {
    file_name: 'Rahul_Mehta.pdf',
    candidate_name: 'Rahul Mehta',
    text: `
Rahul Mehta | Pune, India
ML Engineer
Skills: Python, PyTorch, NLP, SQL, Docker
Experience: 5 years in product analytics and machine learning.
Education: M.Tech Artificial Intelligence
Summary: Trained deep learning models and deployed APIs with FastAPI.
`.trim(),
  },
  {
    file_name: 'Anita_Joshi.pdf',
    candidate_name: 'Anita Joshi',
    text: `
Anita Joshi | Bengaluru, India
Data Analyst
Skills: Python, Excel, Tableau, Data Visualization, SQL
Experience: 3 years in reporting and BI.
Education: B.Sc Statistics
Summary: Created dashboards, cleaned data, and prepared business reports.
`.trim(),
  },
];

export async function fetchHealth(): Promise<boolean> {
  const response = await fetch('/health');
  return response.ok;
}

export async function runDemoMatch(topK: number): Promise<MatchRecord[]> {
  const response = await fetch('/match', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      job_description: DEMO_JOB_DESCRIPTION,
      resumes: DEMO_RESUMES.map((item) => item.text),
      top_k: topK,
    }),
  });

  if (!response.ok) {
    throw new Error('Demo match request failed');
  }

  const payload = await response.json();
  return payload.results as MatchRecord[];
}

export async function runUploadMatch(jobDescription: string, files: File[], topK: number): Promise<MatchRecord[]> {
  const formData = new FormData();
  formData.append('job_description', jobDescription);
  formData.append('top_k', String(topK));
  files.forEach((file) => formData.append('files', file));

  const response = await fetch('/api/v1/match/upload', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Upload match request failed');
  }

  const payload = await response.json();
  return payload.results as MatchRecord[];
}
