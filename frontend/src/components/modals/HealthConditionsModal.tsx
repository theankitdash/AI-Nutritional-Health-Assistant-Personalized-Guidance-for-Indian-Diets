'use client';

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import { getHealthConditions, saveHealthConditions, getPersonalDetails } from '@/lib/api';
import type { HealthConditions } from '@/lib/types';
import { useModalForm } from '@/hooks/useModalForm';
import {
    DIABETES_OPTIONS,
    THYROID_OPTIONS,
    YES_NO_OPTIONS
} from '@/lib/formConstants';
import { SelectField, InputField } from '@/components/ui/FormComponents';
import styles from '@/styles/components/Modal.module.css';

interface HealthConditionsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const initialData: Partial<HealthConditions> = {
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
};

export default function HealthConditionsModal({
    isOpen,
    onClose,
}: HealthConditionsModalProps) {
    const { formData, setFormData, isLoading, isSaving, error, handleSubmit } =
        useModalForm({
            fetchData: getHealthConditions,
            saveData: saveHealthConditions,
            initialData: initialData as HealthConditions,
            isOpen,
            onClose,
        });

    const [showPCOS, setShowPCOS] = useState(false);

    useEffect(() => {
        if (isOpen) {
            checkGenderForPCOS();
        }
    }, [isOpen]);

    const checkGenderForPCOS = async () => {
        try {
            const personalDetails = await getPersonalDetails();
            setShowPCOS(personalDetails.gender === 'female');
        } catch (error) {
            console.error('Error fetching gender for PCOS field:', error);
        }
    };

    const handleChange = (name: string, value: string | number) => {
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Health Conditions">
            <form onSubmit={handleSubmit}>
                {error && (
                    <div style={{ color: 'red', marginBottom: '1rem' }}>
                        Error: {error}
                    </div>
                )}

                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        Loading health conditions...
                    </div>
                ) : (
                    <>
                        <InputField
                            label="Allergies"
                            id="allergies"
                            value={formData.allergies || ''}
                            onChange={handleChange}
                            placeholder="Enter any allergies (e.g., peanuts, shellfish)"
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Diabetes"
                            id="diabetes"
                            value={formData.diabetes || 'none'}
                            options={DIABETES_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Hypertension (High Blood Pressure)"
                            id="hypertension"
                            value={formData.hypertension || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="High Cholesterol"
                            id="cholesterol"
                            value={formData.cholesterol || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Thyroid Disorders"
                            id="thyroid"
                            value={formData.thyroid || 'none'}
                            options={THYROID_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Kidney Disease"
                            id="kidneydisease"
                            value={formData.kidneydisease || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Liver Disease"
                            id="liverdisease"
                            value={formData.liverdisease || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Lactose Intolerance"
                            id="lactoseintolerance"
                            value={formData.lactoseintolerance || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Gluten Sensitivity (Celiac Disease)"
                            id="glutensensitivity"
                            value={formData.glutensensitivity || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        {/* PCOS Field - Only visible for female users */}
                        {showPCOS && (
                            <SelectField
                                label="PCOS/PCOD"
                                id="pcos"
                                value={formData.pcos || 'no'}
                                options={YES_NO_OPTIONS}
                                onChange={handleChange}
                                disabled={isSaving}
                            />
                        )}

                        <SelectField
                            label="Anemia (Iron Deficiency)"
                            id="anemia"
                            value={formData.anemia || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Osteoporosis (Bone Weakness)"
                            id="osteoporosis"
                            value={formData.osteoporosis || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="IBS (Irritable Bowel Syndrome)"
                            id="ibs"
                            value={formData.ibs || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="GERD (Acid Reflux/Heartburn)"
                            id="gerd"
                            value={formData.gerd || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <SelectField
                            label="Gout"
                            id="gout"
                            value={formData.gout || 'no'}
                            options={YES_NO_OPTIONS}
                            onChange={handleChange}
                            disabled={isSaving}
                        />

                        <InputField
                            label="Other Conditions"
                            id="otherconditions"
                            value={formData.otherconditions || ''}
                            onChange={handleChange}
                            placeholder="Enter any other conditions"
                            disabled={isSaving}
                        />

                        <button
                            className={styles.button} // Keep original styling
                            type="submit"
                            disabled={isSaving}
                        >
                            {isSaving ? 'Saving...' : 'Save Health Conditions'}
                        </button>
                    </>
                )}
            </form>
        </Modal>
    );
}
