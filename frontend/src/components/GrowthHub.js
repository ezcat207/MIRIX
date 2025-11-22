import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';
import { format, subDays } from 'date-fns';
import './GrowthHub.css';
import { useTranslation } from 'react-i18next';
import queuedFetch from '../utils/requestQueue';

// Register Chart.js components
ChartJS.register(ArcElement, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const GrowthHub = ({ settings }) => {
  const { t } = useTranslation();
  const [activeSubTab, setActiveSubTab] = useState('daily-review');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));

  // Data states for different subtabs
  const [dailyReviewData, setDailyReviewData] = useState(null);
  const [morningBriefData, setMorningBriefData] = useState(null);
  const [workSessionsData, setWorkSessionsData] = useState([]);
  const [patternsData, setPatternsData] = useState([]);
  const [insightsData, setInsightsData] = useState([]);
  const [projectsData, setProjectsData] = useState([]);

  // Search and filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedItems, setExpandedItems] = useState(new Set());

  // Fetch data based on active subtab
  const fetchData = async (subtab) => {
    try {
      setLoading(true);
      setError(null);

      switch (subtab) {
        case 'daily-review':
          await fetchDailyReview(selectedDate);
          break;
        case 'morning-brief':
          await fetchMorningBrief(selectedDate);
          break;
        case 'work-sessions':
          await fetchWorkSessions(selectedDate);
          break;
        case 'patterns':
          await fetchPatterns(selectedDate);
          break;
        case 'insights':
          await fetchInsights(selectedDate);
          break;
        case 'projects':
          await fetchProjects();
          break;
        default:
          break;
      }
    } catch (err) {
      console.error(`Error fetching ${subtab} data:`, err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch Daily Review data
  const fetchDailyReview = async (date) => {
    const response = await queuedFetch(`${settings.serverUrl}/growth/daily_review?date=${date}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch daily review: ${response.statusText}`);
    }
    const result = await response.json();
    if (!result.success) {
      throw new Error(result.error || 'Failed to load daily review');
    }
    setDailyReviewData(result.data);
  };

  // Fetch Morning Brief data
  const fetchMorningBrief = async (date) => {
    const response = await queuedFetch(`${settings.serverUrl}/growth/morning_brief?date=${date}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch morning brief: ${response.statusText}`);
    }
    const result = await response.json();
    setMorningBriefData(result);
  };

  // Fetch Work Sessions data
  const fetchWorkSessions = async (date) => {
    const response = await queuedFetch(`${settings.serverUrl}/growth/work_sessions?date=${date}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch work sessions: ${response.statusText}`);
    }
    const result = await response.json();
    setWorkSessionsData(result.work_sessions || []);
  };

  // Fetch Patterns data
  const fetchPatterns = async (date) => {
    const response = await queuedFetch(`${settings.serverUrl}/growth/patterns?date=${date}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch patterns: ${response.statusText}`);
    }
    const result = await response.json();
    setPatternsData(result.patterns || []);
  };

  // Fetch Insights data
  const fetchInsights = async (date) => {
    const response = await queuedFetch(`${settings.serverUrl}/growth/insights?date=${date}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch insights: ${response.statusText}`);
    }
    const result = await response.json();
    setInsightsData(result.insights || []);
  };

  // Fetch Projects data
  const fetchProjects = async () => {
    const response = await queuedFetch(`${settings.serverUrl}/dashboard/projects`);
    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    const result = await response.json();
    setProjectsData(result.projects || []);
  };

  // Fetch data when component mounts or active tab changes
  useEffect(() => {
    fetchData(activeSubTab);
    setExpandedItems(new Set());
  }, [activeSubTab, selectedDate, settings.serverUrl]);

  // Handle date change
  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  // Navigate to previous/next day
  const navigateDay = (direction) => {
    const currentDate = new Date(selectedDate);
    const newDate = direction === 'prev'
      ? subDays(currentDate, 1)
      : new Date(currentDate.getTime() + 86400000); // Add 1 day
    setSelectedDate(format(newDate, 'yyyy-MM-dd'));
  };

  // Toggle expand/collapse for items
  const toggleExpanded = (itemId) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  // Helper function to get subtab icon
  const getSubTabIcon = (subtab) => {
    switch (subtab) {
      case 'daily-review': return '📊';
      case 'morning-brief': return '🌅';
      case 'work-sessions': return '⏱️';
      case 'patterns': return '🔄';
      case 'insights': return '💡';
      case 'projects': return '📁';
      default: return '📈';
    }
  };

  // Helper function to get subtab label
  const getSubTabLabel = (subtab) => {
    switch (subtab) {
      case 'daily-review': return 'Daily Review';
      case 'morning-brief': return 'Morning Brief';
      case 'work-sessions': return 'Work Sessions';
      case 'patterns': return 'Patterns';
      case 'insights': return 'Insights';
      case 'projects': return 'Projects';
      default: return subtab;
    }
  };

  // Render content based on active subtab
  const renderContent = () => {
    if (loading) {
      return (
        <div className="growth-loading">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="growth-error">
          <p>Error: {error}</p>
          <button onClick={() => fetchData(activeSubTab)} className="retry-button">
            Retry
          </button>
        </div>
      );
    }

    switch (activeSubTab) {
      case 'daily-review':
        return renderDailyReview();
      case 'morning-brief':
        return renderMorningBrief();
      case 'work-sessions':
        return renderWorkSessions();
      case 'patterns':
        return renderPatterns();
      case 'insights':
        return renderInsights();
      case 'projects':
        return renderProjects();
      default:
        return <div>Select a tab</div>;
    }
  };

  // Render Daily Review content
  const renderDailyReview = () => {
    if (!dailyReviewData) {
      return <div className="growth-empty">No data available for this date.</div>;
    }

    const { time_allocation, efficiency_metrics, patterns, insights, summary } = dailyReviewData;

    return (
      <div className="daily-review-content">
        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Work Hours</div>
            <div className="stat-value">{(time_allocation?.total_work_hours || 0).toFixed(1)}h</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Work Sessions</div>
            <div className="stat-value">{time_allocation?.total_sessions || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Avg Focus Score</div>
            <div className="stat-value">{(efficiency_metrics?.average_focus_score || 0).toFixed(1)}/10</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Deep Work Time</div>
            <div className="stat-value">{((efficiency_metrics?.deep_work_time || 0) / 3600).toFixed(1)}h</div>
          </div>
        </div>

        {/* Summary Section */}
        {summary && (
          <div className="summary-section">
            <h3>📝 Summary</h3>
            <div className="summary-content">{summary}</div>
          </div>
        )}

        {/* Insights Section */}
        {insights && insights.length > 0 && (
          <div className="insights-section">
            <h3>💡 Key Insights</h3>
            <div className="insights-list">
              {insights.map((insight, index) => (
                <div key={index} className="insight-card">
                  <div className="insight-header">
                    <span className="insight-category">{insight.category}</span>
                    <span className="insight-priority">Priority: {insight.priority}/10</span>
                  </div>
                  <h4>{insight.title}</h4>
                  <p>{insight.content}</p>
                  {insight.action_items && insight.action_items.length > 0 && (
                    <div className="action-items">
                      <strong>Action Items:</strong>
                      <ul>
                        {insight.action_items.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Patterns Section */}
        {patterns && patterns.length > 0 && (
          <div className="patterns-section">
            <h3>🔄 Detected Patterns</h3>
            <div className="patterns-list">
              {patterns.map((pattern, index) => (
                <div key={index} className="pattern-card">
                  <h4>{pattern.pattern_type}</h4>
                  <p>{pattern.description}</p>
                  <div className="pattern-meta">
                    <span>Confidence: {(pattern.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render Morning Brief content
  const renderMorningBrief = () => {
    if (!morningBriefData) {
      return <div className="growth-empty">No morning brief available.</div>;
    }

    const { yesterday_summary, today_suggestions, work_sessions, insights } = morningBriefData;

    return (
      <div className="morning-brief-content">
        <div className="brief-header">
          <h2>🌅 Good Morning!</h2>
          <p className="brief-date">{format(new Date(selectedDate), 'EEEE, MMMM d, yyyy')}</p>
        </div>

        {yesterday_summary && (
          <div className="brief-section">
            <h3>📊 Yesterday's Summary</h3>
            <p>{yesterday_summary}</p>
          </div>
        )}

        {today_suggestions && today_suggestions.length > 0 && (
          <div className="brief-section">
            <h3>🎯 Today's Suggestions</h3>
            <ul className="suggestions-list">
              {today_suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}

        {insights && insights.length > 0 && (
          <div className="brief-section">
            <h3>💡 Recent Insights</h3>
            <div className="insights-list">
              {insights.slice(0, 3).map((insight, index) => (
                <div key={index} className="insight-card">
                  <h4>{insight.title}</h4>
                  <p>{insight.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render Work Sessions content
  const renderWorkSessions = () => {
    if (workSessionsData.length === 0) {
      return <div className="growth-empty">No work sessions found for this date.</div>;
    }

    return (
      <div className="work-sessions-content">
        <div className="sessions-list">
          {workSessionsData.map((session, index) => (
            <div key={session.id || index} className="session-card">
              <div className="session-header">
                <span className="session-time">
                  {new Date(session.start_time).toLocaleTimeString()} - {new Date(session.end_time).toLocaleTimeString()}
                </span>
                <span className="session-duration">{Math.round(session.duration / 60)} min</span>
              </div>
              <div className="session-details">
                <div className="session-meta">
                  <span>Activity: {session.activity_type}</span>
                  <span>Focus: {session.focus_score}/10</span>
                </div>
                {session.app_breakdown && Object.keys(session.app_breakdown).length > 0 && (
                  <div className="session-apps">
                    <strong>Apps:</strong> {Object.keys(session.app_breakdown).join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render Patterns content
  const renderPatterns = () => {
    if (patternsData.length === 0) {
      return <div className="growth-empty">No patterns detected for this date.</div>;
    }

    return (
      <div className="patterns-content">
        <div className="patterns-list">
          {patternsData.map((pattern, index) => (
            <div key={pattern.id || index} className="pattern-card">
              <div className="pattern-header">
                <h4>{pattern.pattern_type}</h4>
                <span className="pattern-confidence">{(pattern.confidence * 100).toFixed(0)}%</span>
              </div>
              <p className="pattern-description">{pattern.description}</p>
              {pattern.metadata && (
                <div className="pattern-metadata">
                  <pre>{JSON.stringify(pattern.metadata, null, 2)}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render Insights content
  const renderInsights = () => {
    if (insightsData.length === 0) {
      return <div className="growth-empty">No insights available for this date.</div>;
    }

    return (
      <div className="insights-content">
        <div className="insights-list">
          {insightsData.map((insight, index) => (
            <div key={insight.id || index} className="insight-card">
              <div className="insight-header">
                <span className="insight-category">{insight.category}</span>
                <span className="insight-priority">Priority: {insight.priority}/10</span>
              </div>
              <h4>{insight.title}</h4>
              <p className="insight-content">{insight.content}</p>
              {insight.action_items && insight.action_items.length > 0 && (
                <div className="action-items">
                  <strong>Action Items:</strong>
                  <ul>
                    {insight.action_items.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="insight-meta">
                <span>Impact: {insight.impact_score}/10</span>
                {insight.generated_at && (
                  <span>Generated: {new Date(insight.generated_at).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render Projects content
  const renderProjects = () => {
    if (projectsData.length === 0) {
      return <div className="growth-empty">No projects found.</div>;
    }

    return (
      <div className="projects-content">
        <div className="projects-list">
          {projectsData.map((project, index) => (
            <div key={project.id || index} className="project-card">
              <h4>{project.name}</h4>
              <p className="project-description">{project.description}</p>
              {project.tasks && project.tasks.length > 0 && (
                <div className="project-tasks">
                  <strong>Tasks ({project.tasks.length}):</strong>
                  <ul>
                    {project.tasks.slice(0, 5).map((task, i) => (
                      <li key={i} className={task.completed ? 'completed' : ''}>
                        {task.title}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="growth-hub">
      {/* Header with subtabs */}
      <div className="growth-header">
        <div className="growth-subtabs">
          <div className="growth-subtabs-left">
            {['daily-review', 'morning-brief', 'work-sessions', 'patterns', 'insights', 'projects'].map(subtab => (
              <button
                key={subtab}
                className={`growth-subtab ${activeSubTab === subtab ? 'active' : ''}`}
                onClick={() => setActiveSubTab(subtab)}
              >
                <span className="subtab-icon">{getSubTabIcon(subtab)}</span>
                <span className="subtab-label">{getSubTabLabel(subtab)}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Date selector (for date-specific tabs) */}
        {['daily-review', 'morning-brief', 'work-sessions', 'patterns', 'insights'].includes(activeSubTab) && (
          <div className="date-selector">
            <button onClick={() => navigateDay('prev')} className="nav-button">←</button>
            <input
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              max={format(new Date(), 'yyyy-MM-dd')}
            />
            <button
              onClick={() => navigateDay('next')}
              className="nav-button"
              disabled={selectedDate === format(new Date(), 'yyyy-MM-dd')}
            >
              →
            </button>
          </div>
        )}

        {/* Refresh button */}
        <button
          onClick={() => fetchData(activeSubTab)}
          className="refresh-button"
          disabled={loading}
        >
          🔄 Refresh
        </button>
      </div>

      {/* Content area */}
      <div className="growth-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default GrowthHub;
