'use client';

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import { getPersonalDetails, savePersonalDetails } from '@/lib/api';
import type { PersonalDetails } from '@/lib/types';
import styles from '@/styles/components/Modal.module.css';

interface PersonalDetailsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function PersonalDetailsModal({
    isOpen,
    onClose,
}: PersonalDetailsModalProps) {
    const [formData, setFormData] = useState<PersonalDetails>({
        name: '',
        dateofbirth: '',
        gender: 'male',
        height: 0,
        weight: 0,
        waist: 0,
    });

    useEffect(() => {
        if (isOpen) {
            fetchData();
        }
    }, [isOpen]);

    const fetchData = async () => {
        try {
            const data = await getPersonalDetails();
            setFormData(data);
        } catch (error) {
            console.error('Error fetching personal details:', error);
        }
    };

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

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await savePersonalDetails(formData);
            alert('Profile saved successfully!');
            onClose();
        } catch (error: any) {
            alert(`Error saving profile: ${error.message}`);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Personal Details">
            <form onSubmit={handleSubmit}>
                <div className={styles.setting}>
                    <label htmlFor="name">Full Name:</label>
                    <input
                        type="text"
                        id="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Enter your full name"
                    />
                </div>

                <div className={styles.setting}>
                    <label htmlFor="dateofbirth">Date of Birth:</label>
                    <input
                        type="date"
                        id="dateofbirth"
                        value={formData.dateofbirth}
                        onChange={handleChange}
                    />
                </div>

                <div className={styles.setting}>
                    <label htmlFor="gender">Gender:</label>
                    <select id="gender" value={formData.gender} onChange={handleChange}>
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
                    />
                </div>

                <button className={styles.button} type="submit">
                    Save
                </button>
            </form>
        </Modal>
    );
}
