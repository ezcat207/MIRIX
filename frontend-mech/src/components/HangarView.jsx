import React from 'react';

const HangarView = ({ pilotMetrics, mechs, dailyHistory, onLaunch, onViewStats }) => {
    return (
        <div className="mech-screen screen-hangar active">
            <div className="hangar-header">
                <div style={{ fontFamily: 'var(--font-hud)', color: 'var(--color-hangar)' }}>
          // HANGAR BAY // PRE-FLIGHT CHECK
                </div>
                <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
                    <button
                        onClick={onViewStats}
                        style={{
                            background: 'transparent',
                            border: '1px solid var(--color-debrief)',
                            color: 'var(--color-debrief)',
                            padding: '5px 15px',
                            cursor: 'pointer',
                            fontFamily: 'var(--font-hud)',
                            fontSize: '11px'
                        }}
                    >
                        FLIGHT RECORDER &gt;&gt;
                    </button>
                    <div style={{ fontSize: '12px', color: '#aaa' }}>
                        PILOT: <span style={{ color: '#fff' }}>COMMANDER</span>
                    </div>
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
            <div className="mech-bay" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px' }}>
                {mechs.map((mech) => (
                    <div
                        key={mech.id}
                        className="mech-card"
                        onClick={() => onLaunch(mech.id)}
                        style={{
                            padding: '0',
                            overflow: 'hidden',
                            position: 'relative',
                            height: '280px',
                            display: 'flex',
                            flexDirection: 'column',
                            border: '1px solid #333',
                            background: '#111'
                        }}
                    >
                        {/* Mech Image */}
                        <div style={{
                            height: '140px',
                            background: mech.image ? `url(${mech.image}) center/cover no-repeat` : '#222',
                            borderBottom: '1px solid #333',
                            position: 'relative'
                        }}>
                            <div style={{
                                position: 'absolute',
                                top: '5px',
                                right: '5px',
                                background: 'rgba(0,0,0,0.7)',
                                padding: '2px 5px',
                                fontSize: '10px',
                                color: mech.status === 'Ready' ? 'var(--color-hangar)' : '#888',
                                border: `1px solid ${mech.status === 'Ready' ? 'var(--color-hangar)' : '#444'}`
                            }}>
                                {mech.status.toUpperCase()}
                            </div>
                        </div>

                        {/* Content */}
                        <div style={{ padding: '12px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                            <div style={{ color: 'var(--color-hangar)', fontWeight: 'bold', marginBottom: '5px', fontSize: '14px' }}>
                                {mech.name}
                            </div>
                            <div style={{ fontSize: '10px', color: '#aaa', marginBottom: '8px' }}>
                                {mech.type.toUpperCase()} // MK-II
                            </div>

                            {/* Why Context */}
                            <div style={{ fontSize: '10px', color: '#ddd', marginBottom: 'auto', fontStyle: 'italic', lineHeight: '1.4' }}>
                                "{mech.why || '--'}"
                            </div>

                            <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ fontSize: '10px', color: '#888' }}>
                                    TASKS: {mech.tasks.length}
                                </div>
                                <span style={{ fontSize: '10px', color: 'var(--color-hangar)', fontWeight: 'bold' }}>LAUNCH &gt;&gt;</span>
                            </div>
                        </div>
                    </div>
                ))}
                {mechs.length === 0 && (
                    <div style={{ color: '#aaa', padding: '20px', textAlign: 'center', gridColumn: '1 / -1' }}>
                        No Mechs detected. Check projects.json.
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
