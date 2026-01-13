'use client';

import React from 'react';
import styles from '@/styles/components/Modal.module.css';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: React.ReactNode;
}

export default function Modal({ isOpen, onClose, title, children }: ModalProps) {
    if (!isOpen) return null;

    return (
        <div className={styles.modal}>
            <div className={styles.modalContent}>
                <span className={styles.close} onClick={onClose}>
                    &times;
                </span>
                <h2>{title}</h2>
                {children}
            </div>
        </div>
    );
}
