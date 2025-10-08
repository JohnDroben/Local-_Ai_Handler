import React, { useState } from 'react'
import axios from 'axios'
import Papa from 'papaparse'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default function App() {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [csvFile, setCsvFile] = useState(null)
  const [csvResult, setCsvResult] = useState(null)
  const [error, setError] = useState(null)

  const analyzeName = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const r = await axios.post(`${API_BASE}/analyze-name`, { name })
      setResult(r.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const uploadCsv = (e) => {
    setCsvFile(e.target.files[0])
  }

  const analyzeCsv = async () => {
    if (!csvFile) return
    setLoading(true)
    setError(null)
    try {
      const fd = new FormData()
      fd.append('file', csvFile)
      const r = await axios.post(`${API_BASE}/analyze-csv`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      // The backend returns { filename, content }
      const parsed = Papa.parse(r.data.content, { header: true })
      setCsvResult(parsed.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>Локальный обработчик имён</h1>
        <p className="subtitle">Локальная обработка имён через Ollama</p>
      </header>

      <main className="container">
        <section className="card">
          <h2>Анализ одного имени</h2>
          <form onSubmit={analyzeName} className="form">
            <input value={name} onChange={e=>setName(e.target.value)} placeholder="Введите имя" />
            <button type="submit" disabled={loading}>Анализировать</button>
          </form>
          {loading && <div className="loader">Идёт анализ...</div>}
          {error && <div className="error">{error}</div>}
          {result && (
            <div className="result">
              <div>Пол: {result.gender}</div>
              <div>Официальное имя: {result.full_name}</div>
              <div>Очищённый ввод: {result.corrected_input}</div>
            </div>
          )}
        </section>

        <section className="card">
          <h2>Анализ CSV</h2>
          <input type="file" accept=".csv" onChange={uploadCsv} />
          <button onClick={analyzeCsv} disabled={loading || !csvFile}>Загрузить и анализировать</button>
          {csvResult && (
            <table className="results-table">
              <thead>
                <tr>
                  {Object.keys(csvResult[0]||{}).map(k=> <th key={k}>{k}</th>)}
                </tr>
              </thead>
              <tbody>
                {csvResult.map((r, idx)=> (
                  <tr key={idx}>
                    {Object.values(r).map((v,i)=><td key={i}>{v}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>

      <footer className="footer">Запуск локальной LLM через Ollama обязателен: http://localhost:11434</footer>
    </div>
  )
}
