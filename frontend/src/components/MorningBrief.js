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

  const { greeting, summary, tasks, reminders, insights, motivation } = briefData;

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

      {/* Summary Stats */}
      <div className="summary-section">
        <h2>📊 Today's Overview</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📝</div>
            <div className="stat-content">
              <div className="stat-value">{summary?.total_tasks || 0}</div>
              <div className="stat-label">Total Tasks</div>
            </div>
          </div>
          <div className="stat-card priority">
            <div className="stat-icon">🔥</div>
            <div className="stat-content">
              <div className="stat-value">{summary?.high_priority_tasks || 0}</div>
              <div className="stat-label">High Priority</div>
            </div>
          </div>
          <div className="stat-card overdue">
            <div className="stat-icon">⚠️</div>
            <div className="stat-content">
              <div className="stat-value">{summary?.overdue_tasks || 0}</div>
              <div className="stat-label">Overdue</div>
            </div>
          </div>
          <div className="stat-card time">
            <div className="stat-icon">⏱️</div>
            <div className="stat-content">
              <div className="stat-value">{summary?.time_estimate_hours?.toFixed(1) || 0}h</div>
              <div className="stat-label">Estimated Time</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tasks Sections */}
      <div className="tasks-sections">
        {/* High Priority Tasks */}
        {tasks?.high_priority && tasks.high_priority.length > 0 && (
          <div className="task-section">
            <h3>🔥 High Priority Tasks</h3>
            <div className="task-list">
              {tasks.high_priority.map(renderTaskCard)}
            </div>
          </div>
        )}

        {/* Overdue Tasks */}
        {tasks?.overdue && tasks.overdue.length > 0 && (
          <div className="task-section overdue-section">
            <h3>⚠️ Overdue Tasks</h3>
            <div className="task-list">
              {tasks.overdue.map(renderTaskCard)}
            </div>
          </div>
        )}

        {/* Due Today */}
        {tasks?.due_today && tasks.due_today.length > 0 && (
          <div className="task-section">
            <h3>📅 Due Today</h3>
            <div className="task-list">
              {tasks.due_today.map(renderTaskCard)}
            </div>
          </div>
        )}
      </div>

      {/* Reminders */}
      {reminders && reminders.length > 0 && (
        <div className="reminders-section">
          <h3>🔔 Today's Reminders</h3>
          <div className="reminders-list">
            {reminders.map(renderReminderCard)}
          </div>
        </div>
      )}

      {/* Insights from Yesterday */}
      {insights && insights.length > 0 && (
        <div className="insights-section">
          <h3>💡 Insights from Yesterday</h3>
          <div className="insights-list">
            {insights.map((insight, index) => (
              <div key={index} className="insight-card">
                <span className="insight-icon">💡</span>
                <p>{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Motivation */}
      {motivation && (
        <div className="motivation-section">
          <div className="motivation-card">
            <div className="motivation-icon">🌟</div>
            <p className="motivation-text">{motivation}</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!tasks?.high_priority?.length &&
       !tasks?.overdue?.length &&
       !tasks?.due_today?.length &&
       !reminders?.length && (
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
