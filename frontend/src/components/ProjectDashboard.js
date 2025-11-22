import React, { useState, useEffect } from 'react';
import './ProjectDashboard.css';

const ProjectDashboard = ({ serverUrl }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'board'

  // Fetch projects list
  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${serverUrl}/dashboard/projects`);
      if (!response.ok) {
        throw new Error(`Failed to fetch projects: ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Failed to load projects');
      }

      setProjects(result.projects || []);

      // Auto-select first active project
      if (result.projects && result.projects.length > 0) {
        const activeProject = result.projects.find(p => p.status === 'active') || result.projects[0];
        handleSelectProject(activeProject.id);
      }
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch project dashboard data
  const fetchProjectDashboard = async (projectId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${serverUrl}/dashboard/project/${projectId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch project dashboard: ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Failed to load project dashboard');
      }

      setDashboardData(result.data);
    } catch (err) {
      console.error('Error fetching project dashboard:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle project selection
  const handleSelectProject = (projectId) => {
    setSelectedProject(projectId);
    fetchProjectDashboard(projectId);
  };

  // Initial load
  useEffect(() => {
    fetchProjects();
  }, [serverUrl]);

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#10b981';
      case 'completed':
        return '#6b7280';
      case 'archived':
        return '#9ca3af';
      default:
        return '#3b82f6';
    }
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    if (priority >= 8) return '#ef4444';
    if (priority >= 5) return '#f59e0b';
    return '#3b82f6';
  };

  // Render project list
  const renderProjectList = () => (
    <div className="project-list">
      <div className="project-list-header">
        <h3>Projects</h3>
        <select className="status-filter">
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </select>
      </div>
      <div className="projects-grid">
        {projects.map(project => (
          <div
            key={project.id}
            className={`project-card ${selectedProject === project.id ? 'selected' : ''}`}
            onClick={() => handleSelectProject(project.id)}
          >
            <div className="project-card-header">
              <h4>{project.name}</h4>
              <span
                className="status-badge"
                style={{ backgroundColor: getStatusColor(project.status) }}
              >
                {project.status}
              </span>
            </div>
            {project.description && (
              <p className="project-description">{project.description}</p>
            )}
            <div className="project-meta">
              <div className="meta-item">
                <span className="label">Priority:</span>
                <span
                  className="value priority"
                  style={{ color: getPriorityColor(project.priority || 5) }}
                >
                  {project.priority || 5}/10
                </span>
              </div>
              <div className="meta-item">
                <span className="label">Progress:</span>
                <span className="value">{(project.progress || 0).toFixed(0)}%</span>
              </div>
            </div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${project.progress || 0}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Render task board
  const renderTaskBoard = () => {
    if (!dashboardData || !dashboardData.tasks) return null;

    const { tasks } = dashboardData;
    const columns = [
      { key: 'todo', title: 'To Do', tasks: tasks.todo || [], color: '#6b7280' },
      { key: 'in_progress', title: 'In Progress', tasks: tasks.in_progress || [], color: '#f59e0b' },
      { key: 'completed', title: 'Done', tasks: tasks.completed || [], color: '#10b981' }
    ];

    return (
      <div className="task-board">
        {columns.map(column => (
          <div key={column.key} className="task-column">
            <div className="column-header" style={{ borderTopColor: column.color }}>
              <h4>{column.title}</h4>
              <span className="task-count">{column.tasks.length}</span>
            </div>
            <div className="task-list">
              {column.tasks.map(task => (
                <div key={task.id} className="task-card">
                  <div className="task-header">
                    <h5>{task.title}</h5>
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
                  <div className="task-footer">
                    {task.estimated_hours && (
                      <span className="task-meta">
                        📊 {task.estimated_hours}h est.
                      </span>
                    )}
                    {task.actual_hours && (
                      <span className="task-meta">
                        ⏱️ {task.actual_hours.toFixed(1)}h actual
                      </span>
                    )}
                  </div>
                  {task.is_blocker && (
                    <div className="blocker-badge">🚫 Blocker</div>
                  )}
                </div>
              ))}
              {column.tasks.length === 0 && (
                <div className="empty-column">No tasks</div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Render bottlenecks
  const renderBottlenecks = () => {
    if (!dashboardData || !dashboardData.bottlenecks || dashboardData.bottlenecks.length === 0) {
      return null;
    }

    return (
      <div className="bottlenecks-section">
        <h3>🚨 Bottlenecks</h3>
        <div className="bottlenecks-list">
          {dashboardData.bottlenecks.map((bottleneck, index) => (
            <div key={index} className="bottleneck-card">
              <div className="bottleneck-header">
                <h4>{bottleneck.task_title}</h4>
                <span className="priority-badge high">High Priority</span>
              </div>
              <div className="bottleneck-reasons">
                {bottleneck.reasons.map((reason, idx) => (
                  <span key={idx} className="reason-tag">{reason}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading && !dashboardData) {
    return (
      <div className="project-dashboard-container">
        <div className="loading-message">Loading projects...</div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="project-dashboard-container">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={fetchProjects}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="project-dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <h1>📊 Project Dashboard</h1>
        <div className="view-toggle">
          <button
            className={viewMode === 'list' ? 'active' : ''}
            onClick={() => setViewMode('list')}
          >
            List View
          </button>
          <button
            className={viewMode === 'board' ? 'active' : ''}
            onClick={() => setViewMode('board')}
          >
            Board View
          </button>
        </div>
      </div>

      {/* Project List */}
      {viewMode === 'list' && renderProjectList()}

      {/* Project Dashboard */}
      {selectedProject && dashboardData && (
        <div className="project-detail">
          {/* Project Info */}
          <div className="project-info-card">
            <div className="project-info-header">
              <h2>{dashboardData.project_info?.name}</h2>
              <span
                className="status-badge large"
                style={{ backgroundColor: getStatusColor(dashboardData.project_info?.status) }}
              >
                {dashboardData.project_info?.status}
              </span>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Completion</div>
                <div className="stat-value">
                  {dashboardData.progress?.completion_percentage?.toFixed(0) || 0}%
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Total Tasks</div>
                <div className="stat-value">{dashboardData.progress?.total_tasks || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Completed</div>
                <div className="stat-value success">
                  {dashboardData.progress?.completed_tasks || 0}
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Health Score</div>
                <div className="stat-value health">
                  {dashboardData.health_score?.toFixed(1) || 'N/A'}/10
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="progress-section">
              <div className="progress-label">
                <span>Overall Progress</span>
                <span className="progress-percentage">
                  {dashboardData.progress?.completion_percentage?.toFixed(0) || 0}%
                </span>
              </div>
              <div className="progress-bar-large">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${dashboardData.progress?.completion_percentage || 0}%` }}
                />
              </div>
            </div>

            {/* Time Investment */}
            {dashboardData.time_investment && (
              <div className="time-stats">
                <div className="time-stat">
                  <span className="label">Total Hours:</span>
                  <span className="value">
                    {dashboardData.time_investment.total_hours?.toFixed(1) || 0}h
                  </span>
                </div>
                <div className="time-stat">
                  <span className="label">Avg Hours/Day:</span>
                  <span className="value">
                    {dashboardData.time_investment.avg_hours_per_day?.toFixed(1) || 0}h
                  </span>
                </div>
                <div className="time-stat">
                  <span className="label">Sessions:</span>
                  <span className="value">
                    {dashboardData.time_investment.sessions_count || 0}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Bottlenecks */}
          {renderBottlenecks()}

          {/* Task Board */}
          <div className="board-section">
            <h3>📋 Tasks</h3>
            {renderTaskBoard()}
          </div>

          {/* Velocity */}
          {dashboardData.velocity && (
            <div className="velocity-section">
              <h3>📈 Velocity</h3>
              <div className="velocity-grid">
                <div className="velocity-card">
                  <div className="label">This Week</div>
                  <div className="value">{dashboardData.velocity.tasks_completed_this_week} tasks</div>
                </div>
                <div className="velocity-card">
                  <div className="label">Last Week</div>
                  <div className="value">{dashboardData.velocity.tasks_completed_last_week} tasks</div>
                </div>
                <div className="velocity-card">
                  <div className="label">Avg/Day</div>
                  <div className="value">{dashboardData.velocity.avg_tasks_per_day?.toFixed(1)} tasks</div>
                </div>
                <div className="velocity-card">
                  <div className="label">Trend</div>
                  <div className={`value trend ${dashboardData.velocity.trend}`}>
                    {dashboardData.velocity.trend === 'increasing' && '↗️ Increasing'}
                    {dashboardData.velocity.trend === 'stable' && '→ Stable'}
                    {dashboardData.velocity.trend === 'decreasing' && '↘️ Decreasing'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectDashboard;
