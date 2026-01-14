'use client';

import React from 'react';
import Modal from '@/components/ui/Modal';
import { getPersonalDetails, savePersonalDetails } from '@/lib/api';
import type { PersonalDetails } from '@/lib/types';
import { useModalForm } from '@/hooks/useModalForm';
import styles from '@/styles/components/Modal.module.css';

interface PersonalDetailsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const initialData: PersonalDetails = {
    name: '',
    dateofbirth: '',
    gender: 'male',
    height: 0,
    weight: 0,
    waist: 0,
};

export default function PersonalDetailsModal({
    isOpen,
    onClose,
}: PersonalDetailsModalProps) {
    const { formData, setFormData, isLoading, isSaving, error, handleSubmit } =
        useModalForm({
            fetchData: getPersonalDetails,
            saveData: savePersonalDetails,
            initialData,
            isOpen,
            onClose,
        });

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { id, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [id]: ['height', 'weight', 'waist'].includes(id)
                ? parseFloat(value) || 0
                : value,
        }));
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Personal Details">
            <form onSubmit={handleSubmit}>
                {error && (
                    <div style={{ color: 'red', marginBottom: '1rem' }}>
                        Error: {error}
                    </div>
                )}

                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        Loading...
                    </div>
                ) : (
                    <>
                        <div className={styles.setting}>
                            <label htmlFor="name">Full Name:</label>
                            <input
                                type="text"
                                id="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Enter your full name"
                                disabled={isSaving}
                            />
                        </div>

                        <div className={styles.setting}>
                            <label htmlFor="dateofbirth">Date of Birth:</label>
                            <input
                                type="date"
                                id="dateofbirth"
                                value={formData.dateofbirth}
                                onChange={handleChange}
                                disabled={isSaving}
                            />
                        </div>

                        <div className={styles.setting}>
                            <label htmlFor="gender">Gender:</label>
                            <select
                                id="gender"
                                value={formData.gender}
                                onChange={handleChange}
                                disabled={isSaving}
                            >
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div className={styles.setting}>
                            <label htmlFor="height">Height (in cm):</label>
                            <input
                                type="number"
                                id="height"
                                value={formData.height || ''}
                                onChange={handleChange}
                                placeholder="Enter your height"
                                disabled={isSaving}
                            />
                        </div>

                        <div className={styles.setting}>
                            <label htmlFor="weight">Weight (in kg):</label>
                            <input
                                type="number"
                                id="weight"
                                value={formData.weight || ''}
                                onChange={handleChange}
                                placeholder="Enter your weight"
                                disabled={isSaving}
                            />
                        </div>

                        <div className={styles.setting}>
                            <label htmlFor="waist">Waist (in inches):</label>
                            <input
                                type="number"
                                id="waist"
                                value={formData.waist || ''}
                                onChange={handleChange}
                                placeholder="Enter your waist"
                                disabled={isSaving}
                            />
                        </div>

                        <button
                            className={styles.button}
                            type="submit"
                            disabled={isSaving}
                        >
                            {isSaving ? 'Saving...' : 'Save'}
                        </button>
                    </>
                )}
            </form>
        </Modal>
    );
}
