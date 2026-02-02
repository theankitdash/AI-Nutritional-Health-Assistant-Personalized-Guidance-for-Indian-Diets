'use client';

import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatForm from './ChatForm';
import { sendChatMessage } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { ApiError } from '@/lib/types';
import styles from '@/styles/components/Chat.module.css';

interface Message {
    id?: string;
    sender: 'user' | 'bot';
    text: string;
}

export default function ChatContainer() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { userName } = useAuth();
    const { showToast } = useToast();

    useEffect(() => {
        // Scroll to bottom when messages change
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = async (message: string) => {
        // Add user message to chat
        const userMsgId = Date.now().toString();
        setMessages((prev) => [...prev, { id: userMsgId, sender: 'user', text: message }]);
        setIsLoading(true);

        try {
            // Send message to backend and get response
            const response = await sendChatMessage(message);
            setMessages((prev) => [
                ...prev,
                { id: (Date.now() + 1).toString(), sender: 'bot', text: response.bot_response },
            ]);
        } catch (error: unknown) {
            console.error('Chat error:', error);
            // Show toast for error but also add error message to chat
            const errorMessage = (error as ApiError).message || (error as Error).message || 'Unable to connect to the server';
            showToast(errorMessage, 'error');

            setMessages((prev) => [
                ...prev,
                { id: (Date.now() + 1).toString(), sender: 'bot', text: `Sorry, I encountered an error: ${errorMessage}` },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.chatHeader}>
                <h2>Welcome, {userName}</h2>
            </div>


            <div className={styles.chatMessages}>
                {messages.map((msg, index) => (
                    <ChatMessage key={msg.id || index} sender={msg.sender} text={msg.text} />
                ))}
                {isLoading && (
                    <div style={{ textAlign: 'center', padding: '1rem', color: '#666' }}>
                        Bot is typing...
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <ChatForm onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
    );
}
