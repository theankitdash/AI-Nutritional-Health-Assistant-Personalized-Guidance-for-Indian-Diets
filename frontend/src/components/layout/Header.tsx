'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import styles from '@/styles/components/Header.module.css';

export default function Header() {
    const { logout } = useAuth();

    const handleLogout = async () => {
        try {
            await logout();
            alert('Logout successful.');
            window.location.reload();
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
