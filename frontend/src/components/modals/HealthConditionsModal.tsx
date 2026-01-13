'use client';

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import { getHealthConditions, saveHealthConditions, getPersonalDetails } from '@/lib/api';
import type { HealthConditions } from '@/lib/types';
import styles from '@/styles/components/Modal.module.css';

interface HealthConditionsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function HealthConditionsModal({
    isOpen,
    onClose,
}: HealthConditionsModalProps) {
    const [formData, setFormData] = useState<Partial<HealthConditions>>({
        allergies: '',
        diabetes: 'none',
        hypertension: 'no',
        cholesterol: 'no',
        thyroid: 'none',
        kidneydisease: 'no',
        liverdisease: 'no',
        lactoseintolerance: 'no',
        glutensensitivity: 'no',
        pcos: 'no',
        anemia: 'no',
        osteoporosis: 'no',
        ibs: 'no',
        gerd: 'no',
        gout: 'no',
        otherconditions: '',
    });
    const [showPCOS, setShowPCOS] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchData();
            checkGenderForPCOS();
        }
    }, [isOpen]);

    const fetchData = async () => {
        try {
            const data = await getHealthConditions();
            setFormData(data);
        } catch (error) {
            console.error('Error fetching health conditions:', error);
        }
    };

    const checkGenderForPCOS = async () => {
        try {
            const personalDetails = await getPersonalDetails();
            setShowPCOS(personalDetails.gender === 'female');
        } catch (error) {
            console.error('Error fetching gender for PCOS field:', error);
        }
    };

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { id, value } = e.target;
        setFormData((prev) => ({ ...prev, [id]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await saveHealthConditions(formData as HealthConditions);
            alert('Health conditions saved successfully!');
            onClose();
        } catch (error: any) {
            alert(`Error saving health conditions: ${error.message}`);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Health Conditions">
            <form onSubmit={handleSubmit}>
                <div className={styles.setting}>
                    <label htmlFor="allergies">Allergies:</label>
                    <input
                        type="text"
                        id="allergies"
                        value={formData.allergies || ''}
                        onChange={handleChange}
                        placeholder="Enter any allergies (e.g., peanuts, shellfish)"
                    />
                </div>

                <div className={styles.setting}>
                    <label htmlFor="diabetes">Diabetes:</label>
                    <select id="diabetes" value={formData.diabetes || 'none'} onChange={handleChange}>
                        <option value="none">None</option>
                        <option value="type1">Type 1</option>
                        <option value="type2">Type 2</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="hypertension">Hypertension (High Blood Pressure):</label>
                    <select id="hypertension" value={formData.hypertension || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="cholesterol">High Cholesterol:</label>
                    <select id="cholesterol" value={formData.cholesterol || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="thyroid">Thyroid Disorders:</label>
                    <select id="thyroid" value={formData.thyroid || 'none'} onChange={handleChange}>
                        <option value="none">None</option>
                        <option value="hypothyroidism">Hypothyroidism</option>
                        <option value="hyperthyroidism">Hyperthyroidism</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="kidneydisease">Kidney Disease:</label>
                    <select id="kidneydisease" value={formData.kidneydisease || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="liverdisease">Liver Disease:</label>
                    <select id="liverdisease" value={formData.liverdisease || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="lactoseintolerance">Lactose Intolerance:</label>
                    <select id="lactoseintolerance" value={formData.lactoseintolerance || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="glutensensitivity">Gluten Sensitivity (Celiac Disease):</label>
                    <select id="glutensensitivity" value={formData.glutensensitivity || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                {/* PCOS Field - Only visible for female users */}
                {showPCOS && (
                    <div className={styles.setting}>
                        <label htmlFor="pcos">PCOS/PCOD:</label>
                        <select id="pcos" value={formData.pcos || 'no'} onChange={handleChange}>
                            <option value="no">No</option>
                            <option value="yes">Yes</option>
                        </select>
                    </div>
                )}

                <div className={styles.setting}>
                    <label htmlFor="anemia">Anemia (Iron Deficiency):</label>
                    <select id="anemia" value={formData.anemia || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="osteoporosis">Osteoporosis (Bone Weakness):</label>
                    <select id="osteoporosis" value={formData.osteoporosis || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="ibs">IBS (Irritable Bowel Syndrome):</label>
                    <select id="ibs" value={formData.ibs || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="gerd">GERD (Acid Reflux/Heartburn):</label>
                    <select id="gerd" value={formData.gerd || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="gout">Gout:</label>
                    <select id="gout" value={formData.gout || 'no'} onChange={handleChange}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                    </select>
                </div>

                <div className={styles.setting}>
                    <label htmlFor="otherconditions">Other Conditions:</label>
                    <input
                        type="text"
                        id="otherconditions"
                        value={formData.otherconditions || ''}
                        onChange={handleChange}
                        placeholder="Enter any other conditions"
                    />
                </div>

                <button className={styles.button} type="submit">
                    Save Health Conditions
                </button>
            </form>
        </Modal>
    );
}
