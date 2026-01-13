'use client';

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import { updatePassword } from '@/lib/api';
import { isStrongPassword } from '@/lib/utils';
import styles from '@/styles/components/Modal.module.css';

interface AccountSettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function AccountSettingsModal({
    isOpen,
    onClose,
}: AccountSettingsModalProps) {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [passwordFeedback, setPasswordFeedback] = useState('');

    const handleNewPasswordChange = (value: string) => {
        setNewPassword(value);
        if (isStrongPassword(value)) {
            setPasswordFeedback('Strong password.');
        } else {
            setPasswordFeedback('Weak password. Ensure it meets the requirements.');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!isStrongPassword(newPassword)) {
            alert('Password does not meet the required strength.');
            return;
        }

        try {
            await updatePassword({
                current_password: currentPassword,
                new_password: newPassword,
            });
            alert('Password changed successfully!');
            setCurrentPassword('');
            setNewPassword('');
            setPasswordFeedback('');
            onClose();
        } catch (error: any) {
            alert(`Error: ${error.message}`);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Change Password">
            <form onSubmit={handleSubmit}>
                <div className={styles.setting}>
                    <label htmlFor="currentPassword">Current Password:</label>
                    <input
                        type="password"
                        id="currentPassword"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        placeholder="Enter your current password"
                    />
                </div>

                <div className={styles.setting}>
                    <label htmlFor="newPassword">New Password:</label>
                    <input
                        type="password"
                        id="newPassword"
                        value={newPassword}
                        onChange={(e) => handleNewPasswordChange(e.target.value)}
                        placeholder="Enter your new password"
                    />
                    {passwordFeedback && (
                        <div
                            className={styles.feedback}
                            style={{
                                color: passwordFeedback.includes('Strong') ? 'green' : 'red',
                            }}
                        >
                            {passwordFeedback}
                        </div>
                    )}
                </div>

                <button className={styles.button} type="submit">
                    Change Password
                </button>
            </form>
        </Modal>
    );
}
