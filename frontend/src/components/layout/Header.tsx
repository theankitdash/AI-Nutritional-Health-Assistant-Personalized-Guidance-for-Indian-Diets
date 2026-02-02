'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import styles from '@/styles/components/Header.module.css';

export default function Header() {
    const { logout } = useAuth();
    const { showToast } = useToast();

    const handleLogout = async () => {
        try {
            await logout();
            showToast('Logout successful.', 'info');
            // Give time for toast to show before reload, or remove reload if state update is enough
            setTimeout(() => window.location.reload(), 1000);
        } catch (error: any) {
            console.error('Error during logout:', error);
        }
    };

    return (
        <header className={styles.header}>
            <div className={styles.leftHeader}>
                <h2>&copy; Nutrify-Health.</h2>
            </div>
            <div className={styles.rightHeader}>
                <button className={styles.logoutBtn} onClick={handleLogout}>
                    Logout
                </button>
            </div>
        </header>
    );
}
