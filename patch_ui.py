"""Patch page.tsx to add Report Card button and History tab."""
import re

with open(r'ui-react\app\page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Report Card button before HTML report button
old = '<button onClick={generateHTMLReport} className="btn-primary flex items-center space-x-2">'
new = '''<button onClick={generateReportCard} className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white rounded-xl transition-all mr-3"><Award className="w-4 h-4" /><span className="ml-2">Report Card</span></button>
                    <button onClick={generateHTMLReport} className="btn-primary flex items-center space-x-2">'''
content = content.replace(old, new, 1)

# 2. Add History tab content before </AnimatePresence> (the one before Processing Overlay)
history_tab = '''
          {activeTab === 'history' && (
            <motion.div key="history" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-5xl mx-auto space-y-8">
              <div className="text-center">
                <h2 className="text-4xl font-bold text-white mb-4">Score History</h2>
                <p className="text-gray-400">Track evaluation scores over time</p>
                <button onClick={fetchHistory} className="mt-4 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-gray-300 text-sm transition-all">{historyLoading ? 'Loading...' : 'Refresh'}</button>
              </div>
              {historyData.length > 0 ? (
                <div className="space-y-6">
                  <div className="card-glass p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Score Trend</h3>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={[...historyData].reverse().map((h,i)=>({name:`#${i+1}`,score:h.score}))}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                          <XAxis dataKey="name" tick={{fill:'#9CA3AF',fontSize:12}} />
                          <YAxis domain={[0,10]} tick={{fill:'#9CA3AF',fontSize:12}} />
                          <Tooltip contentStyle={{backgroundColor:'rgba(17,24,39,0.9)',border:'1px solid rgba(139,92,246,0.3)',borderRadius:'12px'}} formatter={(v:any)=>[v?.toFixed(2),'Score']} />
                          <Line type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={3} dot={{fill:'#8b5cf6',r:5}} activeDot={{r:8}} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="card-glass p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Recent Evaluations</h3>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {historyData.map((h,i) => {
                        const gs = getGradeStyle(h.grade || 'C');
                        return (
                          <div key={i} className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all">
                            <div className="flex items-center space-x-4">
                              <span className={`text-lg font-black ${gs.text}`}>{h.grade}</span>
                              <div>
                                <div className="text-sm font-semibold text-white">{h.label}</div>
                                <div className="text-xs text-gray-400">{h.mode} &bull; {h.time}</div>
                              </div>
                            </div>
                            <div className="text-xl font-bold text-primary-400">{h.score.toFixed(2)}/10</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-20">
                  <TrendingUp className="w-24 h-24 text-gray-600 mx-auto mb-6" />
                  <h3 className="text-2xl font-bold text-white mb-4">{historyLoading ? 'Loading...' : 'No history yet'}</h3>
                  <p className="text-gray-400">Run evaluations to see score history here</p>
                </div>
              )}
            </motion.div>
          )}
'''

# Insert before the Processing Overlay comment
content = content.replace('      {/* Processing Overlay */}', history_tab + '      {/* Processing Overlay */}', 1)

# 3. Set historyData after batch demo setResult
batch_anchor = "          setActiveTab('results');\n          setIsProcessing(false);\n\n          return;\n\n        }\n\n        // OCR mode"
batch_replacement = """          setHistoryData(prev => [{score:DEMO_BATCH.average_score,grade:DEMO_BATCH.class_grade,label:DEMO_BATCH.exam_name,mode:'batch',time:new Date().toLocaleString()},...prev]);
          setActiveTab('results');
          setIsProcessing(false);

          return;

        }

        // OCR mode"""
content = content.replace(batch_anchor, batch_replacement, 1)

# 4. Set historyData after OCR demo setResult
ocr_anchor = "          setActiveTab('results');\n          setIsProcessing(false);\n          return;\n\n        }\n        \n        setResult(mockResult);"
ocr_replacement = """          setHistoryData(prev => [{score:demoData.total_score/(demoData.total_marks/10),grade:demoData.grade,label:'OCR Evaluation',mode:'ocr',time:new Date().toLocaleString()},...prev]);
          setActiveTab('results');
          setIsProcessing(false);
          return;

        }
        
        setResult(mockResult);"""
content = content.replace(ocr_anchor, ocr_replacement, 1)

# 5. Set historyData after text demo setResult
text_anchor = "        setResult(mockResult);\n        setActiveTab('results');\n        setIsProcessing(false);\n        return;"
text_replacement = """        setResult(mockResult);
        setHistoryData(prev => [{score:mockResult.score,grade:mockResult.grade,label:mockResult.question||'Text Evaluation',mode:'text',time:new Date().toLocaleString()},...prev]);
        setActiveTab('results');
        setIsProcessing(false);
        return;"""
content = content.replace(text_anchor, text_replacement, 1)

with open(r'ui-react\app\page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
