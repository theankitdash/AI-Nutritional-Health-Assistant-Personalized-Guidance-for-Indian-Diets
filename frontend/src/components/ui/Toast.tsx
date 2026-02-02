'use client';

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import styles from '@/styles/components/Toast.module.css';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastProps {
    message: string;
    type: ToastType;
    onClose: () => void;
    duration?: number;
}

export default function Toast({ message, type, onClose, duration = 3000 }: ToastProps) {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setVisible(false);
            setTimeout(onClose, 300); // Allow time for exit animation
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose]);

    if (typeof document === 'undefined') return null;

    return createPortal(
        <div className={`${styles.toast} ${styles[type]} ${visible ? styles.show : styles.hide}`}>
            <span className={styles.icon}>
                {type === 'success' && '✓'}
                {type === 'error' && '✕'}
                {type === 'info' && 'ℹ'}
            </span>
            <p className={styles.message}>{message}</p>
            <button className={styles.closeBtn} onClick={() => setVisible(false)}>
                &times;
            </button>
        </div>,
        document.body
    );
}
