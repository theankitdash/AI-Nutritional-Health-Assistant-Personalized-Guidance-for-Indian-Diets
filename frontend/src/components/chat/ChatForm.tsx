'use client';

import React, { useState, FormEvent } from 'react';
import styles from '@/styles/components/Chat.module.css';

interface ChatFormProps {
    onSendMessage: (message: string) => void;
}

export default function ChatForm({ onSendMessage }: ChatFormProps) {
    const [message, setMessage] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (message.trim()) {
            onSendMessage(message);
            setMessage('');
        }
    };

    return (
        <form className={styles.chatForm} onSubmit={handleSubmit}>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a message..."
                required
            />
            <button type="submit">Send</button>
        </form>
    );
}
