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
    React.useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleKeyDown);
            // Lock body scroll
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div
            className={styles.modal}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            <div className={styles.modalContent}>
                <button
                    className={styles.close}
                    onClick={onClose}
                    aria-label="Close modal"
                    style={{ background: 'none', border: 'none', padding: 0 }}
                >
                    &times;
                </button>
                <h2 id="modal-title">{title}</h2>
                {children}
            </div>
        </div>
    );
}
