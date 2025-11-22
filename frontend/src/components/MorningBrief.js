import React, { useState, useEffect } from 'react';
import './MorningBrief.css';

const MorningBrief = ({ serverUrl }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [briefData, setBriefData] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update current time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Update every minute

    return () => clearInterval(timer);
  }, []);

  // Fetch morning brief data
  const fetchMorningBrief = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${serverUrl}/growth/morning_brief`);
      if (!response.ok) {
        throw new Error(`Failed to fetch morning brief: ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Failed to load morning brief');
      }

      setBriefData(result.data);
    } catch (err) {
      console.error('Error fetching morning brief:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch data on mount
  useEffect(() => {
    fetchMorningBrief();
  }, [serverUrl]);

  // Get priority color
  const getPriorityColor = (priority) => {
    if (priority >= 8) return '#ef4444';
    if (priority >= 5) return '#f59e0b';
    return '#3b82f6';
  };

  // Format time
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Format date
  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Render task card
  const renderTaskCard = (task) => (
    <div key={task.id} className="task-card">
      <div className="task-header">
        <h4>{task.title}</h4>
        {task.priority && (
          <span
            className="priority-badge"
            style={{ backgroundColor: getPriorityColor(task.priority) }}
          >
            P{task.priority}
          </span>
        )}
      </div>
      {task.description && (
        <p className="task-description">{task.description}</p>
      )}
      <div className="task-meta">
        {task.estimated_hours && (
          <span className="meta-item">
            📊 {task.estimated_hours}h estimated
          </span>
        )}
        {task.project_name && (
          <span className="meta-item">
            📁 {task.project_name}
          </span>
        )}
        {task.due_date && (
          <span className="meta-item">
            📅 Due: {new Date(task.due_date).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );

  // Render reminder card
  const renderReminderCard = (reminder) => (
    <div key={reminder.id} className="reminder-card">
      <div className="reminder-header">
        <span className="reminder-time">
          🕐 {new Date(reminder.trigger_time).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit'
          })}
        </span>
        {reminder.priority && (
          <span
            className="priority-badge small"
            style={{ backgroundColor: getPriorityColor(reminder.priority) }}
          >
            P{reminder.priority}
          </span>
        )}
      </div>
      <p className="reminder-content">{reminder.content}</p>
    </div>
  );

  if (loading) {
    return (
      <div className="morning-brief-container">
        <div className="loading-message">Loading morning brief...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="morning-brief-container">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={fetchMorningBrief}>Retry</button>
        </div>
      </div>
    );
  }

  if (!briefData) {
    return (
      <div className="morning-brief-container">
        <div className="loading-message">No data available</div>
      </div>
    );
  }

  const {
    greeting,
    yesterday_summary,
    today_priorities,
    reminders,
    optimal_schedule,
    motivational_message
  } = briefData;

  return (
    <div className="morning-brief-container">
      {/* Header with greeting and time */}
      <div className="brief-header">
        <div className="greeting-section">
          <h1 className="greeting">{greeting || 'Good Morning!'}</h1>
          <div className="current-time">
            <span className="time">{formatTime(currentTime)}</span>
            <span className="date">{formatDate(currentTime)}</span>
          </div>
        </div>
        <button className="refresh-button" onClick={fetchMorningBrief}>
          🔄 Refresh
        </button>
      </div>

      {/* Yesterday Summary */}
      {yesterday_summary?.available && (
        <div className="yesterday-section">
          <h2>📊 Yesterday's Summary</h2>
          <div className="stats-grid">
            {yesterday_summary.total_sessions !== undefined && (
              <div className="stat-card">
                <div className="stat-icon">📝</div>
                <div className="stat-content">
                  <div className="stat-value">{yesterday_summary.total_sessions || 0}</div>
                  <div className="stat-label">Work Sessions</div>
                </div>
              </div>
            )}
            {yesterday_summary.total_hours !== undefined && (
              <div className="stat-card">
                <div className="stat-icon">⏱️</div>
                <div className="stat-content">
                  <div className="stat-value">{yesterday_summary.total_hours?.toFixed(1) || 0}h</div>
                  <div className="stat-label">Total Hours</div>
                </div>
              </div>
            )}
            {yesterday_summary.focus_score !== undefined && (
              <div className="stat-card">
                <div className="stat-icon">🎯</div>
                <div className="stat-content">
                  <div className="stat-value">{yesterday_summary.focus_score?.toFixed(1) || 0}/10</div>
                  <div className="stat-label">Focus Score</div>
                </div>
              </div>
            )}
            {yesterday_summary.tasks_completed !== undefined && (
              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-content">
                  <div className="stat-value">{yesterday_summary.tasks_completed || 0}</div>
                  <div className="stat-label">Tasks Done</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Today's Priorities */}
      {today_priorities && today_priorities.length > 0 && (
        <div className="task-section">
          <h3>🔥 Today's Priorities</h3>
          <div className="task-list">
            {today_priorities.map(renderTaskCard)}
          </div>
        </div>
      )}

      {/* Optimal Schedule */}
      {optimal_schedule && (
        <div className="schedule-section">
          <h3>⏰ Optimal Schedule</h3>
          {optimal_schedule.high_productivity_hours && optimal_schedule.high_productivity_hours.length > 0 && (
            <div className="productivity-hours">
              <p className="schedule-label">🎯 High Productivity Hours:</p>
              <div className="hours-list">
                {optimal_schedule.high_productivity_hours.map((hour, index) => (
                  <span key={index} className="hour-badge">
                    {hour}:00 - {hour + 1}:00
                  </span>
                ))}
              </div>
            </div>
          )}
          {optimal_schedule.suggested_schedule && optimal_schedule.suggested_schedule.length > 0 && (
            <div className="suggested-schedule">
              <p className="schedule-label">📋 Suggested Schedule:</p>
              <div className="schedule-items">
                {optimal_schedule.suggested_schedule.map((item, index) => (
                  <div key={index} className="schedule-item">
                    <span className="schedule-time">{item.time}</span>
                    <span className="schedule-task">{item.task}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Reminders */}
      {reminders && reminders.length > 0 && (
        <div className="reminders-section">
          <h3>🔔 Today's Reminders</h3>
          <div className="reminders-list">
            {reminders.map(renderReminderCard)}
          </div>
        </div>
      )}

      {/* Motivation */}
      {motivational_message && (
        <div className="motivation-section">
          <div className="motivation-card">
            <div className="motivation-icon">🌟</div>
            <p className="motivation-text">{motivational_message}</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!today_priorities || today_priorities.length === 0) &&
       (!reminders || reminders.length === 0) &&
       (!yesterday_summary || !yesterday_summary.available) && (
        <div className="empty-state">
          <div className="empty-icon">✨</div>
          <h3>You're all caught up!</h3>
          <p>No tasks or reminders for today. Enjoy your day!</p>
        </div>
      )}
    </div>
  );
};

export default MorningBrief;
