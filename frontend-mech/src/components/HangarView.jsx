import React from 'react';

const HangarView = ({ pilotMetrics, mechs, dailyHistory, onLaunch }) => {
    return (
        <div className="mech-screen screen-hangar active">
            <div className="hangar-header">
                <div style={{ fontFamily: 'var(--font-hud)', color: 'var(--color-hangar)' }}>
          // HANGAR BAY // PRE-FLIGHT CHECK
                </div>
                <div style={{ fontSize: '12px', color: '#aaa' }}>
                    PILOT: <span style={{ color: '#fff' }}>COMMANDER</span>
                </div>
            </div>

            {/* Pilot Metrics */}
            <div className="pilot-card">
                <div style={{ color: 'var(--color-hangar)', marginBottom: '15px', fontWeight: 'bold' }}>
                    PILOT METRICS (O2)
                </div>
                <div className="metric-row">
                    <span>CAPABILITY GROWTH</span>
                    <span style={{ color: '#fff' }}>{pilotMetrics?.capability || 0}</span>
                </div>
                <div className="metric-row">
                    <span>WEALTH FLOW</span>
                    <span style={{ color: '#fff' }}>{pilotMetrics?.wealth || 0}</span>
                </div>
                <div className="metric-row">
                    <span>INFLUENCE</span>
                    <span style={{ color: '#fff' }}>{pilotMetrics?.influence || 0}</span>
                </div>

                <div style={{ marginTop: '20px', borderTop: '1px solid #333', paddingTop: '10px' }}>
                    <div style={{ color: 'var(--color-alert)', fontSize: '12px', marginBottom: '5px' }}>
                        KR0 STATUS: ACTIVE REVIEW
                    </div>
                    <div style={{ fontSize: '10px', color: '#aaa' }}>
                        System Ready. Select Mech to initiate.
                    </div>
                </div>
            </div>

            {/* Mech Bay */}
            <div className="mech-bay">
                {mechs.map((mech) => (
                    <div key={mech.id} className="mech-card" onClick={() => onLaunch(mech.id)}>
                        <div style={{ color: 'var(--color-hangar)', fontWeight: 'bold', marginBottom: '5px' }}>
                            {mech.name}
                        </div>
                        <div style={{ fontSize: '12px', color: '#aaa', marginBottom: '10px' }}>
                            {mech.type} // {mech.status}
                        </div>

                        {/* Why & What Context */}
                        <div style={{ fontSize: '11px', color: '#ddd', marginBottom: '5px', fontStyle: 'italic' }}>
                            WHY: {mech.why || '--'}
                        </div>
                        <div style={{ fontSize: '11px', color: '#ddd', marginBottom: '10px' }}>
                            WHAT: {mech.what || '--'}
                        </div>

                        <div style={{ fontSize: '10px', color: '#888' }}>
                            TASKS: {mech.tasks.length}
                        </div>
                        <div style={{ marginTop: '10px', textAlign: 'right' }}>
                            <span style={{ fontSize: '10px', color: 'var(--color-hangar)' }}>LAUNCH &gt;&gt;</span>
                        </div>
                    </div>
                ))}
                {mechs.length === 0 && (
                    <div style={{ color: '#aaa', padding: '20px', textAlign: 'center' }}>
                        No Mechs detected. Check projects.md.
                    </div>
                )}
            </div>
            {/* Right Column: Mission Log */}
            <div className="hangar-panel" style={{ width: '300px', marginLeft: '20px' }}>
                <div className="panel-header">MISSION LOG (TODAY)</div>
                <div className="panel-content">
                    {dailyHistory && dailyHistory.length > 0 ? (
                        <>
                            {/* OKR Related */}
                            <div style={{ marginBottom: '15px' }}>
                                <div style={{ fontSize: '10px', color: 'var(--color-hangar)', marginBottom: '5px' }}>✓ OKR RELATED</div>
                                {dailyHistory.filter(t => t.okr_related).map((task, idx) => (
                                    <div key={idx} style={{ marginBottom: '8px', borderLeft: '2px solid var(--color-hangar)', paddingLeft: '8px' }}>
                                        <div style={{ color: '#fff', fontSize: '13px' }}>{task.title}</div>
                                        <div style={{ color: '#666', fontSize: '10px' }}>
                                            {new Date(task.time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                            {task.mech_id && ` • ${mechs.find(m => m.id === task.mech_id)?.name || 'Unknown'}`}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Non-OKR */}
                            <div>
                                <div style={{ fontSize: '10px', color: '#666', marginBottom: '5px' }}>⊗ NOT OKR RELATED</div>
                                {dailyHistory.filter(t => !t.okr_related).map((task, idx) => (
                                    <div key={idx} style={{ marginBottom: '8px', borderLeft: '2px solid #444', paddingLeft: '8px', opacity: 0.5 }}>
                                        <div style={{ color: '#888', fontSize: '13px' }}>{task.title}</div>
                                        <div style={{ color: '#555', fontSize: '10px' }}>
                                            {new Date(task.time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div style={{ color: '#666', fontStyle: 'italic' }}>No missions completed yet.</div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default HangarView;
