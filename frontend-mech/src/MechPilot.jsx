import React, { useState, useEffect } from 'react';
import HangarView from './components/HangarView';
import CockpitView from './components/CockpitView';
import DebriefView from './components/DebriefView';
import './styles/MechPilot.css';

const API_BASE = '/api'; // Proxy configured in vite.config.js

const MechPilot = () => {
    const [view, setView] = useState('HANGAR'); // HANGAR, COCKPIT, DEBRIEF
    const [status, setStatus] = useState(null);
    const [activeMech, setActiveMech] = useState(null);
    const [sessionData, setSessionData] = useState(null);

    const [error, setError] = useState(null);

    // Poll status
    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch(`${API_BASE}/mech/status`);
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                const data = await res.json();
                setStatus(data);
                setError(null);

                // Only sync view if we're in HANGAR and backend says otherwise
                // This prevents conflicts when user manually navigates
                if (view === 'HANGAR' && data.state.mode === 'COCKPIT' && data.state.active_mech_id) {
                    const mech = data.mechs.find(m => m.id === data.state.active_mech_id);
                    setActiveMech(mech);
                    setView('COCKPIT');
                }
            } catch (err) {
                console.error("Failed to fetch mech status:", err);
                setError(err.message);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 2000);
        return () => clearInterval(interval);
    }, [view]);

    const handleLaunch = async (mechId) => {
        try {
            const res = await fetch(`${API_BASE}/mech/launch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mech_id: mechId })
            });
            if (res.ok) {
                setView('COCKPIT');
                // Optimistic update
                const mech = status.mechs.find(m => m.id === mechId);
                setActiveMech(mech);
            }
        } catch (err) {
            console.error("Launch failed:", err);
        }
    };

    const handleCompleteTask = async (task) => {
        const title = typeof task === 'string' ? task : task.title;
        try {
            await fetch(`${API_BASE}/mech/complete_task`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_title: title })
            });
            // Optimistic update could happen here, but polling will catch it
        } catch (err) {
            console.error("Task completion failed:", err);
        }
    };

    const handleMissionComplete = () => {
        setView('DEBRIEF');
        // In a real app, we'd fetch the session summary from backend here
        // For now, mock it based on local state
        setSessionData({
            tasks_completed: status?.state?.session_data?.tasks_completed || []
        });
    };

    const handleDebriefSubmit = async (data) => {
        try {
            const res = await fetch(`${API_BASE}/mech/debrief`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                setView('HANGAR');
                setActiveMech(null);
            }
        } catch (err) {
            console.error("Debrief failed:", err);
        }
    };

    if (error) return (
        <div className="mech-pilot-container" style={{ justifyContent: 'center', alignItems: 'center', flexDirection: 'column', color: 'var(--color-alert)' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>SYSTEM FAILURE</div>
            <div>{error}</div>
            <div style={{ fontSize: '12px', marginTop: '20px', color: '#aaa' }}>Check backend connection (port 47283)</div>
        </div>
    );

    if (!status) return <div className="mech-pilot-container" style={{ justifyContent: 'center', alignItems: 'center' }}>INITIALIZING SYSTEM...</div>;

    return (
        <div className="mech-pilot-container">
            {view === 'HANGAR' && (
                <HangarView
                    pilotMetrics={status.pilot_metrics}
                    mechs={status.mechs}
                    dailyHistory={status.daily_history}
                    onLaunch={handleLaunch}
                />
            )}

            {view === 'COCKPIT' && (
                <CockpitView
                    activeMech={activeMech}
                    onCompleteTask={handleCompleteTask}
                    onMissionComplete={handleMissionComplete}
                />
            )}

            {view === 'DEBRIEF' && (
                <DebriefView
                    sessionData={sessionData}
                    onSubmit={handleDebriefSubmit}
                />
            )}
        </div>
    );
};

export default MechPilot;
