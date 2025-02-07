import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Input } from './ui/Input';
import { Button } from './ui/Button';
import { ScrollArea } from './ui/ScrollArea';
import { Loader2 } from './ui/Loader';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Welcome to the Financial Analysis Assistant!' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('https://urban-broccoli-65xgp6499xphx6g5-5000.app.github.dev/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input
        }),
      });

      const data = await response.json();
      
      // Filter only assistant2 responses
      if (data.responses) {
        const assistant2Response = data.responses.find(resp => resp.role === 'assistant2');
        if (assistant2Response) {
          setMessages(prev => [...prev, assistant2Response]);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Sorry, there was an error processing your request.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <Card>
        <CardHeader>
          <CardTitle>Financial Analysis Assistant</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] overflow-auto mb-4 p-4 border rounded">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`p-4 mb-2 rounded ${
                  message.role === 'user' 
                    ? 'bg-blue-100 ml-auto max-w-[80%]' 
                    : 'bg-gray-100 max-w-[80%]'
                }`}
              >
                <p>{message.content}</p>
              </div>
            ))}
            {loading && (
              <div className="flex items-center space-x-2">
                <Loader2 className="h-4 w-4" />
                <span>Processing...</span>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about stocks, company analysis, or market insights..."
              className="flex-1"
              disabled={loading}
            />
            <Button type="submit" disabled={loading}>
              Send
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChatInterface;