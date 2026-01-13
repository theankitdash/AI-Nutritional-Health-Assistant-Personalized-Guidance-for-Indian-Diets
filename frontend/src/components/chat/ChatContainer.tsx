'use client';

import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatForm from './ChatForm';
import { sendChatMessage } from '@/lib/api';
import { getPersonalDetails } from '@/lib/api';
import styles from '@/styles/components/Chat.module.css';

interface Message {
    sender: 'user' | 'bot';
    text: string;
}

export default function ChatContainer() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [welcomeName, setWelcomeName] = useState('User');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Fetch personal details to get user name
        const fetchName = async () => {
            try {
                const details = await getPersonalDetails();
                setWelcomeName(details.name || 'User');
            } catch (error) {
                console.error('Error fetching personal details:', error);
            }
        };
        fetchName();
    }, []);

    useEffect(() => {
        // Scroll to bottom when messages change
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = async (message: string) => {
        // Add user message to chat
        setMessages((prev) => [...prev, { sender: 'user', text: message }]);

        try {
            // Send message to backend and get response
            const response = await sendChatMessage(message);
            setMessages((prev) => [
                ...prev,
                { sender: 'bot', text: response.bot_response },
            ]);
        } catch (error: any) {
            setMessages((prev) => [
                ...prev,
                { sender: 'bot', text: 'Error: Unable to connect to the server.' },
            ]);
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.chatHeader}>
                <h2>Welcome, {welcomeName}</h2>
            </div>

            <div className={styles.chatMessages}>
                {messages.map((msg, index) => (
                    <ChatMessage key={index} sender={msg.sender} text={msg.text} />
                ))}
                <div ref={messagesEndRef} />
            </div>

            <ChatForm onSendMessage={handleSendMessage} />
        </div>
    );
}
