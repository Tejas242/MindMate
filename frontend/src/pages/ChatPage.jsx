import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { chatAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  PaperAirplaneIcon,
  ExclamationTriangleIcon,
  HeartIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const ChatPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [interventions, setInterventions] = useState([]);
  const [showCrisisAlert, setShowCrisisAlert] = useState(false);

  useEffect(() => {
    if (sessionId) {
      loadExistingSession();
    } else {
      createNewSession();
    }
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const createNewSession = async () => {
    try {
      const response = await chatAPI.createSession();
      const session = response.data;
      setCurrentSession(session);
      navigate(`/chat/${session.id}`, { replace: true });
      
      // Add welcome message
      setMessages([{
        id: 'welcome',
        sender: 'assistant',
        content: "Hi there! I'm MindMate, your AI companion for mental wellness support. I'm here to listen, provide guidance, and help you navigate any challenges you're facing. How are you feeling today?",
        timestamp: new Date().toISOString(),
      }]);
    } catch (error) {
      console.error('Error creating session:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadExistingSession = async () => {
    try {
      const [messagesResponse] = await Promise.all([
        chatAPI.getSessionMessages(sessionId),
      ]);
      
      setMessages(messagesResponse.data);
      
      // Create a mock session object (you might want to add an endpoint to get session details)
      setCurrentSession({
        id: parseInt(sessionId),
        session_token: 'existing',
        created_at: new Date().toISOString(),
        current_risk_level: 'low',
        risk_score: 0,
        crisis_flagged: false,
      });
    } catch (error) {
      console.error('Error loading session:', error);
      navigate('/chat');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || sending) return;
    
    setSending(true);
    
    try {
      const response = await chatAPI.sendMessage(currentSession.id, newMessage.trim());
      const chatResponse = response.data;
      
      // Add user message
      const userMessage = {
        id: `user-${Date.now()}`,
        sender: 'user',
        content: newMessage.trim(),
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, userMessage, chatResponse.message]);
      
      // Handle interventions
      if (chatResponse.interventions && chatResponse.interventions.length > 0) {
        setInterventions(chatResponse.interventions);
      }
      
      // Handle crisis alert
      if (chatResponse.crisis_alert) {
        setShowCrisisAlert(true);
      }
      
      // Update session risk level
      if (chatResponse.risk_assessment) {
        setCurrentSession(prev => ({
          ...prev,
          current_risk_level: chatResponse.risk_assessment.risk_level,
          risk_score: chatResponse.risk_assessment.overall_risk_score,
          crisis_flagged: chatResponse.crisis_alert,
        }));
      }
      
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
    }
  };

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel) {
      case 'crisis':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading chat..." />;
  }

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-8rem)]">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center mr-3">
            <HeartIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">MindMate</h3>
            <p className="text-sm text-gray-500">Your AI wellness companion</p>
          </div>
        </div>
        
        {currentSession && (
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getRiskLevelColor(currentSession.current_risk_level)}`}>
              {currentSession.current_risk_level} risk
            </span>
            
            {currentSession.crisis_flagged && (
              <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
            )}
          </div>
        )}
      </div>

      {/* Crisis Alert */}
      {showCrisisAlert && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-700">
                <strong>Crisis Support Available:</strong> If you're having thoughts of self-harm or suicide, please reach out for immediate help.
              </p>
              <div className="mt-2 text-sm text-red-600">
                <p>• Call 988 (Suicide & Crisis Lifeline)</p>
                <p>• Text HOME to 741741 (Crisis Text Line)</p>
                <p>• Call 911 for emergencies</p>
              </div>
              <button
                onClick={() => setShowCrisisAlert(false)}
                className="mt-2 text-xs text-red-600 underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-900 shadow'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {format(new Date(message.timestamp), 'h:mm a')}
              </p>
            </div>
          </div>
        ))}
        
        {sending && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-900 shadow px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Interventions */}
      {interventions.length > 0 && (
        <div className="bg-blue-50 border-t border-blue-200 p-4">
          <div className="flex items-center mb-2">
            <LightBulbIcon className="w-5 h-5 text-blue-600 mr-2" />
            <h4 className="text-sm font-medium text-blue-900">Suggested Wellness Activities</h4>
          </div>
          <div className="space-y-2">
            {interventions.slice(0, 2).map((intervention) => (
              <div key={intervention.id} className="bg-white rounded-lg p-3 shadow-sm">
                <h5 className="text-sm font-medium text-gray-900">{intervention.name}</h5>
                <p className="text-xs text-gray-600 mt-1">{intervention.description}</p>
                <button className="text-xs text-blue-600 mt-2 hover:text-blue-800">
                  Try this activity →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="bg-white border-t border-gray-200 p-4">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={sending}
          />
          <button
            type="submit"
            disabled={!newMessage.trim() || sending}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500 text-center">
          MindMate is here to support you, but is not a replacement for professional mental health care.
        </div>
      </form>
    </div>
  );
};

export default ChatPage;