'use client';

import React, { useState } from 'react';
import styles from '@/styles/components/Chat.module.css';

interface ChatFormProps {
    onSendMessage: (message: string) => void;
    disabled?: boolean;
}

export default function ChatForm({ onSendMessage, disabled = false }: ChatFormProps) {
    const [input, setInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !disabled) {
            onSendMessage(input);
            setInput('');
        }
    };

    return (
        <form className={styles.chatForm} onSubmit={handleSubmit}>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                disabled={disabled}
                className={styles.chatInput}
            />
            <button
                type="submit"
                disabled={disabled || !input.trim()}
                className={styles.chatButton}
            >
                {disabled ? 'Sending...' : 'Send'}
            </button>
        </form>
    );
}
