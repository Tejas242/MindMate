import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { chatAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  ChatBubbleLeftRightIcon,
  HeartIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSessions: 0,
    lastSession: null,
    avgRiskLevel: 'low',
  });

  useEffect(() => {
    fetchUserSessions();
  }, []);

  const fetchUserSessions = async () => {
    try {
      const response = await chatAPI.getUserSessions(5);
      setSessions(response.data);
      
      // Calculate stats
      const totalSessions = response.data.length;
      const lastSession = response.data[0] || null;
      
      setStats({
        totalSessions,
        lastSession,
        avgRiskLevel: lastSession?.current_risk_level || 'low',
      });
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
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

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    let greeting = 'Hello';
    
    if (hour < 12) greeting = 'Good morning';
    else if (hour < 18) greeting = 'Good afternoon';
    else greeting = 'Good evening';
    
    return `${greeting}, ${user.full_name || user.username}!`;
  };

  if (loading) {
    return <LoadingSpinner text="Loading your dashboard..." />;
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">{getWelcomeMessage()}</h1>
        <p className="text-blue-100 mb-4">
          How are you feeling today? I'm here to support you whenever you need someone to talk to.
        </p>
        <Link
          to="/chat"
          className="inline-flex items-center px-4 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
        >
          <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
          Start a conversation
        </Link>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ChatBubbleLeftRightIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalSessions}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <HeartIcon className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Wellness Level</p>
              <p className={`text-2xl font-bold capitalize ${getRiskLevelColor(stats.avgRiskLevel).split(' ')[0]}`}>
                {stats.avgRiskLevel === 'low' ? 'Good' : stats.avgRiskLevel}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ClockIcon className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Last Chat</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.lastSession 
                  ? format(new Date(stats.lastSession.created_at), 'MM/dd') 
                  : 'Never'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Conversations</h2>
        </div>
        
        {sessions.length === 0 ? (
          <div className="p-6 text-center">
            <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <ChatBubbleLeftRightIcon className="w-6 h-6 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No conversations yet</h3>
            <p className="text-gray-500 mb-4">Start your first conversation with MindMate!</p>
            <Link
              to="/chat"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Start chatting
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {sessions.map((session) => (
              <Link
                key={session.id}
                to={`/chat/${session.id}`}
                className="block p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg mr-4">
                      <ChatBubbleLeftRightIcon className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Chat Session
                      </p>
                      <p className="text-sm text-gray-500">
                        {format(new Date(session.created_at), 'MMM dd, yyyy - h:mm a')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getRiskLevelColor(session.current_risk_level)}`}>
                      {session.current_risk_level}
                    </span>
                    
                    {session.crisis_flagged && (
                      <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Wellness Tips */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Daily Wellness Tips</h2>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-sm font-medium text-blue-600">1</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">Take deep breaths</h3>
              <p className="text-sm text-gray-500">Try the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8.</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-sm font-medium text-green-600">2</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">Stay connected</h3>
              <p className="text-sm text-gray-500">Reach out to friends, family, or talk to me whenever you need support.</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-sm font-medium text-purple-600">3</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">Practice gratitude</h3>
              <p className="text-sm text-gray-500">Write down three things you're grateful for today.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Crisis Resources */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center mb-3">
          <ExclamationTriangleIcon className="w-6 h-6 text-red-600 mr-2" />
          <h2 className="text-lg font-medium text-red-900">Need immediate help?</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-medium text-red-900">Crisis Text Line</p>
            <p className="text-red-700">Text HOME to 741741</p>
          </div>
          <div>
            <p className="font-medium text-red-900">National Suicide Prevention Lifeline</p>
            <p className="text-red-700">Call or text 988</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;