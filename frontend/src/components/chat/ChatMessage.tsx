'use client';

import React from 'react';
import styles from '@/styles/components/Chat.module.css';

interface ChatMessageProps {
    sender: 'user' | 'bot';
    text: string;
}

export default function ChatMessage({ sender, text }: ChatMessageProps) {
    return (
        <div className={`${styles.chatMessage} ${styles[sender]}`}>
            <div className={styles.messageContent}>{text}</div>
        </div>
    );
}
