import React, { useState, useEffect } from 'react';

const CockpitView = ({ activeMech, onCompleteTask, onMissionComplete }) => {
    const [sessionTime, setSessionTime] = useState(0);
    const [shieldIntegrity, setShieldIntegrity] = useState(100);

    // Timer
    useEffect(() => {
        const interval = setInterval(() => {
            setSessionTime((prev) => prev + 1);
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    // Format time HH:MM:SS
    const formatTime = (seconds) => {
        const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
        const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    };

    // Get current focus task (first incomplete task)
    const currentTask = activeMech?.tasks && activeMech.tasks.length > 0
        ? activeMech.tasks[0]
        : "FREE FLIGHT MODE";

    const taskTitle = typeof currentTask === 'string' ? currentTask : currentTask.title || currentTask;
    const taskHow = typeof currentTask === 'object' ? currentTask.how : null;
    const taskPrompt = typeof currentTask === 'object' ? currentTask.prompt : null;

    return (
        <div className="mech-screen screen-cockpit active">
            {/* Top Bar */}
            <div style={{ gridColumn: '1/-1', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-cockpit)', padding: '0 20px' }}>
                <div style={{ color: 'var(--color-cockpit)', fontFamily: 'var(--font-hud)' }}>
          // COMBAT MODE // <span style={{ color: '#fff' }}>{activeMech?.name || 'UNKNOWN'}</span>
                </div>
                <button className="mech-btn btn-cockpit" onClick={onMissionComplete}>
                    MISSION COMPLETE
                </button>
            </div>

            {/* Left HUD */}
            <div className="hud-panel" style={{ gridRow: '2/3' }}>
                <div style={{ color: 'var(--color-cockpit)', marginBottom: '10px' }}>TACTICAL MAP</div>
                <div style={{ fontSize: '12px', color: '#aaa', maxHeight: '300px', overflowY: 'auto' }}>
                    {activeMech?.tasks?.map((t, i) => (
                        <div key={i} style={{ marginBottom: '10px', borderBottom: '1px solid #333', paddingBottom: '5px' }}>
                            <div style={{ color: i === 0 ? '#fff' : '#aaa' }}>&gt; {t.title || t}</div>
                            {t.how && <div style={{ fontSize: '10px', color: '#888', marginTop: '2px' }}>HOW: {t.how}</div>}
                            {t.prompt && <div style={{ fontSize: '10px', color: 'var(--color-cockpit)', marginTop: '2px' }}>PROMPT: {t.prompt.substring(0, 30)}...</div>}
                        </div>
                    ))}
                </div>
            </div>

            {/* Center Reticle */}
            <div className="reticle-container">
                <div className="reticle">
                    <div style={{ color: 'var(--color-cockpit)', fontSize: '10px', marginBottom: '10px' }}>
                        CURRENT OBJECTIVE
                    </div>
                    <div className="focus-task">
                        {taskTitle}
                    </div>

                    <button
                        className="mech-btn btn-cockpit"
                        style={{ fontSize: '10px', padding: '4px 8px', marginTop: '10px' }}
                        onClick={() => onCompleteTask(currentTask)}
                    >
                        MARK COMPLETE
                    </button>

                    <div className="shield-bar">
                        <div className="shield-fill" style={{ width: `${shieldIntegrity}%` }}></div>
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--color-cockpit)', marginTop: '5px' }}>
                        FLOW SHIELD: {shieldIntegrity}%
                    </div>
                </div>
            </div>

            {/* Right HUD */}
            <div className="hud-panel" style={{ gridRow: '2/3' }}>
                <div style={{ color: 'var(--color-cockpit)', marginBottom: '10px' }}>SYSTEMS</div>
                <div style={{ fontSize: '12px', marginBottom: '5px' }}>
                    SESSION TIME: <span style={{ color: '#fff' }}>{formatTime(sessionTime)}</span>
                </div>
                <div style={{ fontSize: '12px' }}>
                    FOCUS SCORE: <span style={{ color: '#fff' }}>{shieldIntegrity}%</span>
                </div>

                {/* Active Prompt Context */}
                {taskPrompt && (
                    <div style={{ marginTop: '20px', borderTop: '1px solid #333', paddingTop: '10px' }}>
                        <div style={{ fontSize: '10px', color: 'var(--color-cockpit)', marginBottom: '5px' }}>ACTIVE PROMPT</div>
                        <div style={{ fontSize: '10px', color: '#aaa', fontStyle: 'italic' }}>
                            "{taskPrompt}"
                        </div>
                        <button className="mech-btn btn-cockpit" style={{ fontSize: '9px', marginTop: '5px', width: '100%' }}>
                            COPY TO CLIPBOARD
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CockpitView;
