import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { counsellorAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  ExclamationTriangleIcon,
  UserGroupIcon,
  ClipboardDocumentCheckIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const CounsellorDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [highRiskSessions, setHighRiskSessions] = useState([]);
  const [assignments, setAssignments] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, highRiskResponse, assignmentsResponse] = await Promise.all([
        counsellorAPI.getCounsellorStats(),
        counsellorAPI.getHighRiskSessions(false), // Get all high-risk sessions
        counsellorAPI.getMyAssignments('pending'),
      ]);

      setStats(statsResponse.data);
      setHighRiskSessions(highRiskResponse.data.slice(0, 5)); // Show top 5
      setAssignments(assignmentsResponse.data.slice(0, 5)); // Show top 5
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignToMe = async (studentId, sessionId) => {
    try {
      await counsellorAPI.createAssignment({
        student_id: studentId,
        session_id: sessionId,
        priority: 'high',
      });
      
      // Refresh data
      fetchDashboardData();
    } catch (error) {
      console.error('Error creating assignment:', error);
    }
  };

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel) {
      case 'crisis':
        return 'text-red-600 bg-red-100';
      case 'high':
        return 'text-orange-600 bg-orange-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-green-600 bg-green-100';
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading counsellor dashboard..." />;
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Welcome, {user.full_name || user.username}
        </h1>
        <p className="text-green-100">
          Your counsellor dashboard - helping students in need of support.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ClipboardDocumentCheckIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Assignments</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_assignments || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pending_assignments || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <ExclamationTriangleIcon className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Crisis Cases</p>
              <p className="text-2xl font-bold text-gray-900">{stats.crisis_assignments || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Resolved</p>
              <p className="text-2xl font-bold text-gray-900">{stats.resolved_assignments || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* High Risk Sessions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-medium text-gray-900">High Risk Sessions</h2>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            {highRiskSessions.length} Active
          </span>
        </div>
        
        {highRiskSessions.length === 0 ? (
          <div className="p-6 text-center">
            <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <ChartBarIcon className="w-6 h-6 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No high-risk sessions</h3>
            <p className="text-gray-500">All students are currently in a safe range.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {highRiskSessions.map((item) => (
              <div key={item.session.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="p-2 bg-red-100 rounded-lg mr-4">
                      <UserGroupIcon className="w-5 h-5 text-red-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {item.user_info.username}
                        {item.user_info.campus && ` • ${item.user_info.campus}`}
                      </p>
                      <p className="text-sm text-gray-500">
                        Last active: {format(new Date(item.session.updated_at), 'MMM dd, h:mm a')}
                      </p>
                      <p className="text-sm text-gray-500">
                        Messages: {item.messages_count} • Risk Score: {(item.latest_assessment.overall_risk_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getRiskLevelColor(item.latest_assessment.risk_level)}`}>
                      {item.latest_assessment.risk_level}
                    </span>
                    
                    {!item.assigned_counsellor && (
                      <button
                        onClick={() => handleAssignToMe(item.user_info.id, item.session.id)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-white bg-green-600 hover:bg-green-700"
                      >
                        Assign to me
                      </button>
                    )}
                    
                    {item.assigned_counsellor && (
                      <span className="text-xs text-gray-500">
                        Assigned to: {item.assigned_counsellor}
                      </span>
                    )}
                  </div>
                </div>
                
                {item.latest_assessment.explanation && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-md">
                    <p className="text-sm text-gray-700">
                      <strong>Assessment:</strong> {item.latest_assessment.explanation}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* My Assignments */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">My Pending Assignments</h2>
        </div>
        
        {assignments.length === 0 ? (
          <div className="p-6 text-center">
            <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <ClipboardDocumentCheckIcon className="w-6 h-6 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No pending assignments</h3>
            <p className="text-gray-500">You're all caught up! Check back later for new cases.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {assignments.map((assignment) => (
              <div key={assignment.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Assignment #{assignment.id}
                    </p>
                    <p className="text-sm text-gray-500">
                      Assigned: {format(new Date(assignment.assigned_at), 'MMM dd, h:mm a')}
                    </p>
                    <p className="text-sm text-gray-500">
                      Priority: <span className="capitalize font-medium">{assignment.priority}</span>
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                      ${assignment.priority === 'crisis' ? 'bg-red-100 text-red-800' :
                        assignment.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                        'bg-yellow-100 text-yellow-800'}`}>
                      {assignment.priority}
                    </span>
                    
                    <button className="inline-flex items-center px-3 py-1 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50">
                      View Details
                    </button>
                  </div>
                </div>
                
                {assignment.notes && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-md">
                    <p className="text-sm text-gray-700">
                      <strong>Notes:</strong> {assignment.notes}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-left">
            <UserGroupIcon className="w-6 h-6 text-blue-600 mb-2" />
            <h3 className="font-medium text-gray-900">View All Students</h3>
            <p className="text-sm text-gray-500">See all students and their wellness status</p>
          </button>
          
          <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-left">
            <ChartBarIcon className="w-6 h-6 text-green-600 mb-2" />
            <h3 className="font-medium text-gray-900">Analytics</h3>
            <p className="text-sm text-gray-500">View campus mental health trends</p>
          </button>
          
          <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-left">
            <ClipboardDocumentCheckIcon className="w-6 h-6 text-purple-600 mb-2" />
            <h3 className="font-medium text-gray-900">Generate Report</h3>
            <p className="text-sm text-gray-500">Create wellness summary reports</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CounsellorDashboard;