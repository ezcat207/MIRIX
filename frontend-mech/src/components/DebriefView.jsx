import React, { useState, useEffect } from 'react';

const DebriefView = ({ sessionData, onSubmit }) => {
    const [reflection, setReflection] = useState('');
    const [wealthInput, setWealthInput] = useState('');
    const [influenceInput, setInfluenceInput] = useState('');
    const [oracleQuestion, setOracleQuestion] = useState(null);
    const [loadingQuestion, setLoadingQuestion] = useState(true);

    // Fetch Oracle reflection question
    useEffect(() => {
        const fetchQuestion = async () => {
            try {
                const duration = sessionData?.duration_minutes || Math.floor((Date.now() - (sessionData?.start_time || Date.now())) / 60000);

                const res = await fetch('/api/mech/oracle/reflection', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task_title: sessionData?.task_title || 'Task',
                        duration_minutes: duration,
                        project_why: sessionData?.project_why,
                        project_what: sessionData?.project_what
                    })
                });

                const data = await res.json();
                setOracleQuestion(data.question);
            } catch (err) {
                console.error('Failed to fetch Oracle question:', err);
                setOracleQuestion('What was the most valuable insight from this task?');
            } finally {
                setLoadingQuestion(false);
            }
        };

        fetchQuestion();
    }, [sessionData]);

    const handleSubmit = () => {
        onSubmit({
            reflection,
            metrics: {
                wealth: parseFloat(wealthInput) || 0,
                influence: parseFloat(influenceInput) || 0
            }
        });
    };

    return (
        <div className="mech-screen screen-debrief active">
            <div style={{ textAlign: 'center', fontFamily: 'var(--font-hud)', fontSize: '24px', color: 'var(--color-debrief)' }}>
        // MISSION DEBRIEF //
            </div>

            <div className="report-card">
                <div style={{ marginBottom: '10px', color: '#aaa' }}>MISSION SUMMARY</div>
                <div style={{ fontSize: '18px', marginBottom: '20px' }}>
                    Completed {sessionData?.tasks_completed?.length || 0} tasks.
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div>
                        <div style={{ fontSize: '12px', color: '#aaa' }}>CAPABILITY GROWTH</div>
                        <div className="growth-stat">+0.5% (Auto-Calc)</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '12px', color: '#aaa' }}>FOCUS SCORE</div>
                        <div className="growth-stat">98%</div>
                    </div>
                </div>
            </div>

            {/* Manual Metric Input */}
            <div className="report-card" style={{ borderColor: '#fff' }}>
                <div style={{ marginBottom: '10px', color: '#fff' }}>MANUAL METRIC ENTRY</div>

                <div style={{ marginBottom: '15px' }}>
                    <div style={{ fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>MISSION REFLECTION</div>

                    {/* Oracle Question */}
                    {loadingQuestion ? (
                        <div style={{ fontSize: '11px', color: 'var(--color-debrief)', marginBottom: '8px', fontStyle: 'italic' }}>
                            🔮 Oracle is generating your reflection question...
                        </div>
                    ) : oracleQuestion && (
                        <div style={{
                            fontSize: '12px',
                            color: 'var(--color-debrief)',
                            marginBottom: '10px',
                            padding: '10px',
                            background: 'rgba(255, 107, 107, 0.1)',
                            border: '1px solid var(--color-debrief)',
                            borderRadius: '4px'
                        }}>
                            <div style={{ fontSize: '10px', marginBottom: '5px', opacity: 0.7 }}>🔮 ORACLE QUESTION:</div>
                            <div style={{ fontStyle: 'italic' }}>{oracleQuestion}</div>
                        </div>
                    )}

                    <textarea
                        className="mech-input"
                        style={{ width: '100%', height: '100px', resize: 'vertical' }}
                        placeholder={oracleQuestion || "What went well? What could be improved?"}
                        value={reflection}
                        onChange={(e) => setReflection(e.target.value)}
                    ></textarea>
                </div>

                <div style={{ marginBottom: '15px' }}>
                    <div style={{ fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>WEALTH GENERATED ($)</div>
                    <input
                        type="number"
                        className="mech-input"
                        placeholder="e.g. 100"
                        value={wealthInput}
                        onChange={(e) => setWealthInput(e.target.value)}
                    />
                </div>

                <div>
                    <div style={{ fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>INFLUENCE (NEW FOLLOWERS)</div>
                    <input
                        type="number"
                        className="mech-input"
                        placeholder="e.g. 5"
                        value={influenceInput}
                        onChange={(e) => setInfluenceInput(e.target.value)}
                    />
                </div>
            </div>

            <div className="report-card" style={{ borderColor: 'var(--color-alert)' }}>
                <div style={{ marginBottom: '10px', color: 'var(--color-alert)' }}>KR0: ACTIVE REVIEW REQUIRED</div>
                <div style={{ fontSize: '14px', marginBottom: '10px' }}>Oracle: "What was the biggest blocker during this session?"</div>
                <textarea
                    style={{ width: '100%', height: '80px', background: '#222', border: '1px solid #555', color: '#fff', padding: '10px', fontFamily: 'var(--font-ui)' }}
                    placeholder="Type your reflection here..."
                    value={reflection}
                    onChange={(e) => setReflection(e.target.value)}
                ></textarea>
            </div>

            <div style={{ textAlign: 'center' }}>
                <button className="mech-btn btn-debrief" onClick={handleSubmit}>
                    CONFIRM & RETURN TO HANGAR
                </button>
            </div>
        </div>
    );
};

export default DebriefView;
