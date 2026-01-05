import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Database, Search, BarChart3, Activity, RefreshCw, Loader2, CheckCircle2, AlertCircle, FileText, TrendingUp } from 'lucide-react'
import api from '../services/api'

const Developer = () => {
  const [knowledgeBase, setKnowledgeBase] = useState<any>(null)
  const [ragTest, setRagTest] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [pipeline, setPipeline] = useState<any>(null)
  const [recentAnalyses, setRecentAnalyses] = useState<any>(null)
  const [systemHealth, setSystemHealth] = useState<any>(null)
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({})
  const [ragQuery, setRagQuery] = useState('employment contract software engineer')
  const [ragResults, setRagResults] = useState(5)

  const fetchData = async (endpoint: string, key: string) => {
    setLoading(prev => ({ ...prev, [key]: true }))
    try {
      const response = await api.get(endpoint)
      return response.data
    } catch (error: any) {
      console.error(`Error fetching ${key}:`, error)
      return { error: error.response?.data?.detail || error.message }
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }))
    }
  }

  const loadKnowledgeBase = async () => {
    const data = await fetchData('/api/debug/knowledge-base', 'knowledgeBase')
    setKnowledgeBase(data)
  }

  const loadRAGTest = async () => {
    const data = await fetchData(`/api/debug/test-rag?query=${encodeURIComponent(ragQuery)}&n_results=${ragResults}`, 'ragTest')
    setRagTest(data)
  }

  const loadStats = async () => {
    const data = await fetchData('/api/debug/stats?field_name=salary', 'stats')
    setStats(data)
  }

  const loadPipeline = async () => {
    const data = await fetchData('/api/debug/analysis-pipeline', 'pipeline')
    setPipeline(data)
  }

  const loadRecentAnalyses = async () => {
    const data = await fetchData('/api/debug/recent-analyses?limit=5', 'recentAnalyses')
    setRecentAnalyses(data)
  }

  const loadSystemHealth = async () => {
    const data = await fetchData('/api/debug/system-health', 'systemHealth')
    setSystemHealth(data)
  }

  const loadAll = async () => {
    await Promise.all([
      loadKnowledgeBase(),
      loadPipeline(),
      loadRecentAnalyses(),
      loadSystemHealth(),
    ])
  }

  useEffect(() => {
    loadAll()
  }, [])

  return (
    <div className="min-h-screen pt-24 pb-24 px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-4xl font-bold mb-2">Developer Dashboard</h1>
            <p className="text-gray-400">Monitor RAG model, data sources, and backend operations</p>
          </div>
          <motion.button
            onClick={loadAll}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-4 py-2 bg-gold-500/20 text-gold-400 rounded-lg hover:bg-gold-500/30 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading.knowledgeBase ? 'animate-spin' : ''}`} />
            Refresh All
          </motion.button>
        </motion.div>

        {/* System Health */}
        {systemHealth && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-effect rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-6 h-6 text-gold-500" />
              <h2 className="text-2xl font-semibold">System Health</h2>
            </div>
            {systemHealth.components && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {systemHealth.components.chromadb.status === 'ok' ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-yellow-400" />
                    )}
                    <span className="font-semibold">ChromaDB</span>
                  </div>
                  <div className="text-2xl font-bold text-gold-400">
                    {systemHealth.components.chromadb.chunks}
                  </div>
                  <div className="text-sm text-gray-400">chunks</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {systemHealth.components.knowledge_base.status === 'ready' ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-400" />
                    )}
                    <span className="font-semibold">Knowledge Base</span>
                  </div>
                  <div className="text-2xl font-bold text-gold-400">
                    {systemHealth.components.knowledge_base.processed_contracts}
                  </div>
                  <div className="text-sm text-gray-400">contracts processed</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-blue-400" />
                    <span className="font-semibold">Raw Contracts</span>
                  </div>
                  <div className="text-2xl font-bold text-gold-400">
                    {systemHealth.components.knowledge_base.raw_contracts}
                  </div>
                  <div className="text-sm text-gray-400">files in folder</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {systemHealth.components.embedding_service.status === 'ok' ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-400" />
                    )}
                    <span className="font-semibold">Embeddings</span>
                  </div>
                  <div className="text-sm text-gold-400 capitalize">
                    {systemHealth.components.embedding_service.status}
                  </div>
                </div>
              </div>
            )}
            {systemHealth.recommendations && (
              <div className="mt-4 space-y-1">
                {systemHealth.recommendations.map((rec: string, idx: number) => (
                  <div key={idx} className="text-sm text-gray-400">• {rec}</div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Knowledge Base */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Database className="w-6 h-6 text-gold-500" />
              <h2 className="text-2xl font-semibold">Knowledge Base</h2>
            </div>
            <button
              onClick={loadKnowledgeBase}
              disabled={loading.knowledgeBase}
              className="px-3 py-1 text-sm bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors disabled:opacity-50"
            >
              {loading.knowledgeBase ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Refresh'}
            </button>
          </div>
          {knowledgeBase && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-gold-400">
                    {knowledgeBase.chromadb?.total_chunks || 0}
                  </div>
                  <div className="text-sm text-gray-400">Total Chunks in ChromaDB</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-gold-400">
                    {knowledgeBase.processed_contracts?.count || 0}
                  </div>
                  <div className="text-sm text-gray-400">Processed Contracts</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-gold-400">
                    {knowledgeBase.raw_contracts?.count || 0}
                  </div>
                  <div className="text-sm text-gray-400">Raw Contracts</div>
                </div>
              </div>
              {knowledgeBase.processed_contracts?.contracts && knowledgeBase.processed_contracts.contracts.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Processed Contracts:</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {knowledgeBase.processed_contracts.contracts.map((contract: any, idx: number) => (
                      <div key={idx} className="bg-dark-700/30 rounded-lg p-3 text-sm">
                        <div className="font-medium">{contract.filename}</div>
                        <div className="text-gray-400 text-xs mt-1">
                          Type: {contract.metadata?.contract_type || 'Unknown'} | 
                          Industry: {contract.metadata?.industry || 'Unknown'} | 
                          Chunks: {contract.num_chunks}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>

        {/* RAG Test */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Search className="w-6 h-6 text-gold-500" />
              <h2 className="text-2xl font-semibold">RAG Model Test</h2>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                placeholder="Enter query to test RAG retrieval..."
                className="flex-1 bg-dark-700/50 border border-dark-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gold-500/50"
              />
              <input
                type="number"
                value={ragResults}
                onChange={(e) => setRagResults(parseInt(e.target.value) || 5)}
                min="1"
                max="20"
                className="w-20 bg-dark-700/50 border border-dark-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-gold-500/50"
              />
              <button
                onClick={loadRAGTest}
                disabled={loading.ragTest}
                className="px-4 py-2 bg-gold-500/20 text-gold-400 rounded-lg hover:bg-gold-500/30 transition-colors disabled:opacity-50"
              >
                {loading.ragTest ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Test'}
              </button>
            </div>
            {ragTest && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-dark-700/50 rounded-lg p-3">
                    <div className="text-sm text-gray-400">Query</div>
                    <div className="font-medium">{ragTest.query}</div>
                  </div>
                  <div className="bg-dark-700/50 rounded-lg p-3">
                    <div className="text-sm text-gray-400">Results Found</div>
                    <div className="font-medium text-gold-400">{ragTest.n_results_returned}</div>
                  </div>
                  <div className="bg-dark-700/50 rounded-lg p-3">
                    <div className="text-sm text-gray-400">Embedding Shape</div>
                    <div className="font-medium">{ragTest.query_embedding_shape?.join(' x ')}</div>
                  </div>
                </div>
                {ragTest.results && ragTest.results.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2">Retrieved Contracts:</h3>
                    <div className="space-y-2">
                      {ragTest.results.map((result: any, idx: number) => (
                        <div key={idx} className="bg-dark-700/30 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="font-medium">{result.contract_id}</div>
                            <div className="text-gold-400 font-bold">{result.similarity_score}% match</div>
                          </div>
                          <div className="text-sm text-gray-400 mb-2">
                            Clause: {result.clause_type} | Type: {result.metadata?.contract_type || 'Unknown'}
                          </div>
                          <div className="text-sm text-gray-300 bg-dark-800/50 rounded p-2">
                            {result.text_preview}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {ragTest.results && ragTest.results.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    No results found. Make sure contracts are ingested into the knowledge base.
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>

        {/* Statistics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-6 h-6 text-gold-500" />
              <h2 className="text-2xl font-semibold">Market Statistics</h2>
            </div>
            <button
              onClick={loadStats}
              disabled={loading.stats}
              className="px-3 py-1 text-sm bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors disabled:opacity-50"
            >
              {loading.stats ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Refresh'}
            </button>
          </div>
          {stats && stats.data && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-dark-700/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Total Values</div>
                  <div className="text-xl font-bold text-gold-400">{stats.data.total_values}</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Valid Values</div>
                  <div className="text-xl font-bold text-gold-400">{stats.data.valid_values}</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Median</div>
                  <div className="text-xl font-bold text-gold-400">₹{stats.data.statistics?.median?.toLocaleString() || 0}</div>
                </div>
                <div className="bg-dark-700/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Mean</div>
                  <div className="text-xl font-bold text-gold-400">₹{stats.data.statistics?.mean?.toLocaleString() || 0}</div>
                </div>
              </div>
              {stats.data.all_values && stats.data.all_values.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Sample Values (first 20):</h3>
                  <div className="flex flex-wrap gap-2">
                    {stats.data.all_values.slice(0, 20).map((value: number, idx: number) => (
                      <span key={idx} className="px-2 py-1 bg-dark-700/50 rounded text-sm">
                        ₹{value.toLocaleString()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>

        {/* Analysis Pipeline */}
        {pipeline && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="glass-effect rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-6 h-6 text-gold-500" />
              <h2 className="text-2xl font-semibold">Analysis Pipeline</h2>
            </div>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Pipeline Steps:</h3>
                <ol className="list-decimal list-inside space-y-2">
                  {pipeline.pipeline?.steps?.map((step: string, idx: number) => (
                    <li key={idx} className="text-gray-300">{step}</li>
                  ))}
                </ol>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Configuration:</h3>
                <div className="bg-dark-700/50 rounded-lg p-4 space-y-2 text-sm">
                  {Object.entries(pipeline.pipeline?.config || {}).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-400">{key}:</span>
                      <span className="text-gold-400">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Capabilities:</h3>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(pipeline.pipeline?.capabilities || {}).map(([key, value]) => (
                    <div
                      key={key}
                      className={`px-3 py-1 rounded-lg text-sm ${
                        value ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                      }`}
                    >
                      {key}: {value ? '✓' : '✗'}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Recent Analyses */}
        {recentAnalyses && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="glass-effect rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-gold-500" />
                <h2 className="text-2xl font-semibold">Recent Analyses</h2>
              </div>
              <button
                onClick={loadRecentAnalyses}
                disabled={loading.recentAnalyses}
                className="px-3 py-1 text-sm bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors disabled:opacity-50"
              >
                {loading.recentAnalyses ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Refresh'}
              </button>
            </div>
            {recentAnalyses.analyses && recentAnalyses.analyses.length > 0 ? (
              <div className="space-y-3">
                {recentAnalyses.analyses.map((analysis: any) => (
                  <div key={analysis.id} className="bg-dark-700/30 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">{analysis.filename}</div>
                      <div className="text-gold-400 font-bold">{analysis.fairness_score}%</div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-400">
                      <div>Type: {analysis.contract_type || 'N/A'}</div>
                      <div>Industry: {analysis.industry || 'N/A'}</div>
                      <div>Similar Contracts: {analysis.similar_contracts_count || 0}</div>
                      <div>Red Flags: {analysis.red_flags_count || 0}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                No analyses yet. Upload a contract to see analysis history.
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default Developer

