import React from 'react';

const HangarView = ({ pilotMetrics, mechs, onLaunch }) => {
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
        </div>
    );
};

export default HangarView;
