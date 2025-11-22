import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Line } from 'react-chartjs-2';
import { format, subDays } from 'date-fns';
import './GrowthReview.css';

// Register Chart.js components
ChartJS.register(ArcElement, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const GrowthReview = ({ serverUrl }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [reviewData, setReviewData] = useState(null);
  const [viewMode, setViewMode] = useState('daily'); // 'daily' or 'weekly'

  // Fetch daily review data
  const fetchDailyReview = async (date) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${serverUrl}/growth/daily_review?date=${date}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch daily review: ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Failed to load daily review');
      }

      setReviewData(result.data);
    } catch (err) {
      console.error('Error fetching daily review:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    if (viewMode === 'daily') {
      fetchDailyReview(selectedDate);
    }
  }, [selectedDate, viewMode, serverUrl]);

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

  // Prepare time allocation pie chart data
  const getTimeAllocationData = () => {
    if (!reviewData || !reviewData.time_allocation) return null;

    const timeAllocation = reviewData.time_allocation;
    const sessionsByActivity = timeAllocation.sessions_by_activity_type || {};

    return {
      labels: Object.keys(sessionsByActivity).map(key =>
        key.charAt(0).toUpperCase() + key.slice(1)
      ),
      datasets: [{
        label: 'Hours',
        data: Object.values(sessionsByActivity).map(sessions =>
          sessions.reduce((sum, s) => sum + (s.duration_seconds || 0), 0) / 3600
        ),
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
        ],
        borderWidth: 1,
      }],
    };
  };

  // Prepare efficiency trend line chart data (hourly breakdown)
  const getEfficiencyTrendData = () => {
    if (!reviewData || !reviewData.work_sessions) return null;

    const sessions = reviewData.work_sessions;
    const hourlyFocus = new Array(24).fill(0);
    const hourlyCounts = new Array(24).fill(0);

    sessions.forEach(session => {
      if (session.start_time) {
        const hour = new Date(session.start_time).getHours();
        hourlyFocus[hour] += session.focus_score || 0;
        hourlyCounts[hour]++;
      }
    });

    const avgFocusByHour = hourlyFocus.map((total, hour) =>
      hourlyCounts[hour] > 0 ? total / hourlyCounts[hour] : 0
    );

    return {
      labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
      datasets: [{
        label: 'Average Focus Score',
        data: avgFocusByHour,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
      }],
    };
  };

  if (loading) {
    return (
      <div className="growth-review-container">
        <div className="loading-message">Loading growth review...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="growth-review-container">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={() => fetchDailyReview(selectedDate)}>Retry</button>
        </div>
      </div>
    );
  }

  if (!reviewData) {
    return (
      <div className="growth-review-container">
        <div className="no-data-message">No data available for this date.</div>
      </div>
    );
  }

  const timeAllocationData = getTimeAllocationData();
  const efficiencyTrendData = getEfficiencyTrendData();
  const { time_allocation, efficiency, patterns, insights, summary } = reviewData;

  return (
    <div className="growth-review-container">
      {/* Header with date navigation */}
      <div className="review-header">
        <h1>📊 Growth Review</h1>
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
      </div>

      {/* Time Allocation Summary */}
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
          <div className="stat-label">Avg Session</div>
          <div className="stat-value">{(time_allocation?.average_session_minutes || 0).toFixed(0)}min</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Efficiency Rating</div>
          <div className="stat-value">{efficiency?.efficiency_rating || 'N/A'}</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        {/* Time Allocation Pie Chart */}
        {timeAllocationData && (
          <div className="chart-card">
            <h3>⏱️ Time Allocation by Activity</h3>
            <div className="chart-container">
              <Pie data={timeAllocationData} options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                  tooltip: {
                    callbacks: {
                      label: (context) => {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        return `${label}: ${value.toFixed(1)}h`;
                      }
                    }
                  }
                }
              }} />
            </div>
          </div>
        )}

        {/* Efficiency Trend Line Chart */}
        {efficiencyTrendData && (
          <div className="chart-card">
            <h3>📈 Focus Score Throughout Day</h3>
            <div className="chart-container">
              <Line data={efficiencyTrendData} options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                      display: true,
                      text: 'Focus Score (0-10)'
                    }
                  },
                  x: {
                    title: {
                      display: true,
                      text: 'Hour of Day'
                    }
                  }
                },
                plugins: {
                  legend: {
                    display: false,
                  }
                }
              }} />
            </div>
          </div>
        )}
      </div>

      {/* Efficiency Details */}
      {efficiency && (
        <div className="section-card">
          <h3>📈 Efficiency Analysis</h3>
          <div className="efficiency-grid">
            <div className="efficiency-item">
              <span className="label">Average Focus Score:</span>
              <span className="value">{(efficiency.average_focus_score || 0).toFixed(1)}/10</span>
            </div>
            <div className="efficiency-item">
              <span className="label">Deep Work Hours:</span>
              <span className="value">{(efficiency.deep_work_hours || 0).toFixed(1)}h ({(efficiency.deep_work_percentage || 0).toFixed(1)}%)</span>
            </div>
            <div className="efficiency-item">
              <span className="label">Efficiency Rating:</span>
              <span className="value rating">{efficiency.efficiency_rating || 'N/A'}</span>
            </div>
          </div>
        </div>
      )}

      {/* AI Summary */}
      {summary && (
        <div className="section-card summary-card">
          <h3>✨ AI Summary</h3>
          <div className="summary-content">
            {summary}
          </div>
        </div>
      )}

      {/* Patterns */}
      {patterns && patterns.length > 0 && (
        <div className="section-card">
          <h3>🔍 Patterns Detected</h3>
          <div className="patterns-list">
            {patterns.slice(0, 5).map((pattern, index) => (
              <div key={index} className="pattern-item">
                <div className="pattern-header">
                  <span className="pattern-type">{pattern.pattern_type}</span>
                  <span className="pattern-confidence">
                    {(pattern.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <div className="pattern-description">{pattern.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insights */}
      {insights && insights.length > 0 && (
        <div className="section-card">
          <h3>💡 Insights & Recommendations</h3>
          <div className="insights-list">
            {insights.slice(0, 5).map((insight, index) => (
              <div key={index} className="insight-item">
                <div className="insight-header">
                  <span className="insight-title">{insight.title}</span>
                  <span className="insight-priority">Priority: {insight.priority || 5}/10</span>
                </div>
                <div className="insight-content">{insight.content}</div>
                {insight.actionable && (
                  <div className="insight-action">
                    <strong>Action:</strong> {insight.action}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GrowthReview;
