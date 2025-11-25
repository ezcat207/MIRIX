import React from 'react';

const StatsView = ({ sessions, onBack }) => {
    // Calculate aggregated stats
    const totalSessions = sessions.length;
    const totalTasks = sessions.reduce((sum, s) => sum + (s.tasks_completed?.length || 0), 0);
    const totalWealth = sessions.reduce((sum, s) => sum + (s.wealth_generated || 0), 0);
    const totalInfluence = sessions.reduce((sum, s) => sum + (s.influence_gained || 0), 0);
    const avgFocus = totalSessions > 0
        ? sessions.reduce((sum, s) => sum + (s.focus_score || 0), 0) / totalSessions
        : 0;

    // Get recent sessions (last 7)
    const recentSessions = sessions.slice(-7).reverse();

    return (
        <div className="mech-screen screen-stats active">
            <div className="hangar-header">
                <div style={{ fontFamily: 'var(--font-hud)', color: 'var(--color-debrief)' }}>
                    // FLIGHT RECORDER // HISTORICAL DATA
                </div>
                <button
                    onClick={onBack}
                    style={{
                        background: 'transparent',
                        border: '1px solid var(--color-debrief)',
                        color: 'var(--color-debrief)',
                        padding: '5px 15px',
                        cursor: 'pointer',
                        fontFamily: 'var(--font-hud)',
                        fontSize: '12px'
                    }}
                >
                    &lt;&lt; RETURN TO HANGAR
                </button>
            </div>

            {/* Summary Cards */}
            <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                <div className="pilot-card" style={{ flex: 1 }}>
                    <div style={{ color: 'var(--color-debrief)', fontSize: '12px', marginBottom: '5px' }}>TOTAL SESSIONS</div>
                    <div style={{ fontSize: '32px', color: '#fff' }}>{totalSessions}</div>
                </div>
                <div className="pilot-card" style={{ flex: 1 }}>
                    <div style={{ color: 'var(--color-debrief)', fontSize: '12px', marginBottom: '5px' }}>TASKS COMPLETED</div>
                    <div style={{ fontSize: '32px', color: '#fff' }}>{totalTasks}</div>
                </div>
                <div className="pilot-card" style={{ flex: 1 }}>
                    <div style={{ color: 'var(--color-debrief)', fontSize: '12px', marginBottom: '5px' }}>TOTAL WEALTH</div>
                    <div style={{ fontSize: '32px', color: '#fff' }}>{totalWealth.toFixed(1)}</div>
                </div>
                <div className="pilot-card" style={{ flex: 1 }}>
                    <div style={{ color: 'var(--color-debrief)', fontSize: '12px', marginBottom: '5px' }}>AVG FOCUS</div>
                    <div style={{ fontSize: '32px', color: '#fff' }}>{avgFocus.toFixed(0)}%</div>
                </div>
            </div>

            {/* Recent Sessions */}
            <div className="pilot-card">
                <div style={{ color: 'var(--color-debrief)', marginBottom: '15px', fontWeight: 'bold' }}>
                    RECENT SESSIONS
                </div>
                {recentSessions.length > 0 ? (
                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        {recentSessions.map((session, idx) => (
                            <div
                                key={session.id || idx}
                                style={{
                                    borderBottom: '1px solid #333',
                                    padding: '15px 0',
                                    marginBottom: '10px'
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <div>
                                        <div style={{ color: '#fff', fontSize: '14px', marginBottom: '5px' }}>
                                            Session {recentSessions.length - idx}
                                        </div>
                                        <div style={{ color: '#888', fontSize: '11px' }}>
                                            {new Date(session.start_time).toLocaleString('en-US', {
                                                month: 'short',
                                                day: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            })}
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ color: 'var(--color-debrief)', fontSize: '12px' }}>
                                            {session.tasks_completed?.length || 0} tasks
                                        </div>
                                        <div style={{ color: '#888', fontSize: '11px' }}>
                                            {Math.round((new Date(session.end_time) - new Date(session.start_time)) / 60000)} min
                                        </div>
                                    </div>
                                </div>

                                {/* Metrics */}
                                <div style={{ display: 'flex', gap: '15px', fontSize: '11px', marginBottom: '10px' }}>
                                    <div>
                                        <span style={{ color: '#888' }}>Wealth: </span>
                                        <span style={{ color: '#fff' }}>{session.wealth_generated || 0}</span>
                                    </div>
                                    <div>
                                        <span style={{ color: '#888' }}>Influence: </span>
                                        <span style={{ color: '#fff' }}>{session.influence_gained || 0}</span>
                                    </div>
                                    <div>
                                        <span style={{ color: '#888' }}>Focus: </span>
                                        <span style={{ color: '#fff' }}>{session.focus_score || 0}%</span>
                                    </div>
                                </div>

                                {/* Reflection */}
                                {session.reflection && (
                                    <div style={{
                                        fontSize: '11px',
                                        color: '#aaa',
                                        fontStyle: 'italic',
                                        borderLeft: '2px solid var(--color-debrief)',
                                        paddingLeft: '10px'
                                    }}>
                                        "{session.reflection}"
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ color: '#666', textAlign: 'center', padding: '40px' }}>
                        No session data available yet.
                    </div>
                )}
            </div>
        </div>
    );
};

export default StatsView;
