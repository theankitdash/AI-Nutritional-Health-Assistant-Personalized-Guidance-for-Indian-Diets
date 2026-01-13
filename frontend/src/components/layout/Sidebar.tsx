'use client';

import React from 'react';
import styles from '@/styles/components/Sidebar.module.css';

interface SidebarProps {
    onOpenPersonalDetails: () => void;
    onOpenPreferences: () => void;
    onOpenHealthConditions: () => void;
    onOpenAccountSettings: () => void;
}

export default function Sidebar({
    onOpenPersonalDetails,
    onOpenPreferences,
    onOpenHealthConditions,
    onOpenAccountSettings,
}: SidebarProps) {
    return (
        <aside className={styles.sidebar}>
            <ul className={styles.sidebarMenu}>
                <li>
                    <button onClick={onOpenPersonalDetails}>Personal Details</button>
                </li>
                <li>
                    <button onClick={onOpenPreferences}>Preferences</button>
                </li>
                <li>
                    <button onClick={onOpenHealthConditions}>Health Conditions</button>
                </li>
                <li>
                    <button onClick={onOpenAccountSettings}>Account Settings</button>
                </li>
            </ul>
        </aside>
    );
}
