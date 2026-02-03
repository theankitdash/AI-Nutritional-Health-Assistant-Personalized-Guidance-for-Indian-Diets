'use client';

import React from 'react';
import Modal from '@/components/ui/Modal';
import { getPreferences, savePreferences } from '@/lib/api';
import type { Preferences } from '@/lib/types';
import { useModalForm } from '@/hooks/useModalForm';
import styles from '@/styles/components/Modal.module.css';
import {
    FOOD_PREFERENCES,
    SNACK_PREFERENCES,
    MEAL_TIMINGS,
    CHEAT_DAY_FREQUENCY,
    CULTURAL_PREFERENCES,
    PREFERRED_INGREDIENTS,
    CUISINE_PREFERENCES,
    SPICY_TOLERANCE,
    MEAL_TYPES,
    FAVORITE_MEALS,
    MEAL_FREQUENCY,
    SWEET_PREFERENCE,
    EATING_OUT_FREQUENCY,
    PREFERRED_DRINKS,
    ACTIVITY_LEVELS,
    FITNESS_GOALS,
    FOOD_RESTRICTIONS,
    CAFFEINE_INTAKE,
    SLEEP_QUALITY,
    SUPPLEMENT_USAGE,
    SUPPLEMENT_FREQUENCY
} from '@/lib/formConstants';
import { RadioGroup, CheckboxGroup, SelectField, InputField } from '@/components/ui/FormComponents';

interface PreferencesModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const initialData: Partial<Preferences> = {
    foodpreference: '',
    snackpreferences: '',
    mealtimings: '',
    cheatdayfrequency: '',
    culturalpreferences: '',
    preferredingredients: '',
    cuisinepreferences: '',
    spicyfoodtolerance: 'Medium',
    preferredmealtype: 'Light',
    favoritemeal: 'Breakfast',
    mealfrequency: '3',
    sweetpreference: 'Regular Sugar',
    eatingoutfrequency: 'Rarely',
    hydrationlevel: 0,
    preferreddrinks: '',
    activitylevel: 'Sedentary',
    fitnessgoal: 'Maintenance',
    foodrestrictions: '',
    caffeineintake: 'Low',
    averagesleep: 0,
    sleepquality: 'Average',
    supplementusage: '',
    supplementfrequency: 'Daily',
};

export default function PreferencesModal({
    isOpen,
    onClose,
}: PreferencesModalProps) {
    const { formData, setFormData, isLoading, isSaving, error, handleSubmit } =
        useModalForm({
            fetchData: getPreferences,
            saveData: savePreferences,
            initialData: initialData as Preferences,
            isOpen,
            onClose,
        });

    const handleCheckboxChange = (name: string, value: string, checked: boolean) => {
        setFormData((prev) => {
            const currentValues = prev[name as keyof Preferences] as string || '';
            const valuesArray = currentValues ? currentValues.split(', ') : [];

            if (checked) {
                if (!valuesArray.includes(value)) {
                    valuesArray.push(value);
                }
            } else {
                const index = valuesArray.indexOf(value);
                if (index > -1) {
                    valuesArray.splice(index, 1);
                }
            }

            return { ...prev, [name]: valuesArray.join(', ') };
        });
    };

    const handleRadioChange = (name: string, value: string) => {
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleInputChange = (name: string, value: string | number) => {
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Preferences">
            <form onSubmit={handleSubmit}>
                {error && (
                    <div style={{ color: 'red', marginBottom: '1rem' }}>
                        Error: {error}
                    </div>
                )}

                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        Loading preferences...
                    </div>
                ) : (
                    <>
                        <RadioGroup
                            label="Food Preference"
                            name="foodpreference"
                            options={FOOD_PREFERENCES}
                            selectedValue={formData.foodpreference}
                            onChange={handleRadioChange}
                        />

                        <CheckboxGroup
                            label="Snack Preferences"
                            name="snackpreferences"
                            options={SNACK_PREFERENCES}
                            selectedValues={formData.snackpreferences}
                            onChange={handleCheckboxChange}
                        />

                        <CheckboxGroup
                            label="Meal Timings"
                            name="mealtimings"
                            options={MEAL_TIMINGS}
                            selectedValues={formData.mealtimings}
                            onChange={handleCheckboxChange}
                        />

                        <RadioGroup
                            label="Cheat Day Frequency"
                            name="cheatdayfrequency"
                            options={CHEAT_DAY_FREQUENCY}
                            selectedValue={formData.cheatdayfrequency}
                            onChange={handleRadioChange}
                        />

                        <CheckboxGroup
                            label="Cultural/Regional Food Preferences"
                            name="culturalpreferences"
                            options={CULTURAL_PREFERENCES}
                            selectedValues={formData.culturalpreferences}
                            onChange={handleCheckboxChange}
                        />

                        <CheckboxGroup
                            label="Preferred Ingredients / Superfoods"
                            name="preferredingredients"
                            options={PREFERRED_INGREDIENTS}
                            selectedValues={formData.preferredingredients}
                            onChange={handleCheckboxChange}
                        />

                        <CheckboxGroup
                            label="Cuisine Preferences"
                            name="cuisinepreferences"
                            options={CUISINE_PREFERENCES}
                            selectedValues={formData.cuisinepreferences}
                            onChange={handleCheckboxChange}
                        />

                        <SelectField
                            label="Spicy Food Tolerance"
                            id="spicyfoodtolerance"
                            value={formData.spicyfoodtolerance}
                            options={SPICY_TOLERANCE}
                            onChange={handleInputChange}
                        />

                        <SelectField
                            label="Preferred Meal Type"
                            id="preferredmealtype"
                            value={formData.preferredmealtype}
                            options={MEAL_TYPES}
                            onChange={handleInputChange}
                        />

                        <SelectField
                            label="Favorite Meal"
                            id="favoritemeal"
                            value={formData.favoritemeal}
                            options={FAVORITE_MEALS}
                            onChange={handleInputChange}
                        />

                        <RadioGroup
                            label="Meal Frequency"
                            name="mealfrequency"
                            options={MEAL_FREQUENCY}
                            selectedValue={formData.mealfrequency}
                            onChange={handleRadioChange}
                        />

                        <RadioGroup
                            label="Sweet Preference"
                            name="sweetpreference"
                            options={SWEET_PREFERENCE}
                            selectedValue={formData.sweetpreference}
                            onChange={handleRadioChange}
                        />

                        <RadioGroup
                            label="Eating Out Frequency"
                            name="eatingoutfrequency"
                            options={EATING_OUT_FREQUENCY}
                            selectedValue={formData.eatingoutfrequency}
                            onChange={handleRadioChange}
                        />

                        <InputField
                            label="Daily Water Intake (L)"
                            id="hydrationlevel"
                            type="number"
                            value={formData.hydrationlevel}
                            onChange={handleInputChange}
                            min="0"
                        />

                        <CheckboxGroup
                            label="Preferred Drinks"
                            name="preferreddrinks"
                            options={PREFERRED_DRINKS}
                            selectedValues={formData.preferreddrinks}
                            onChange={handleCheckboxChange}
                        />

                        <SelectField
                            label="Activity Level"
                            id="activitylevel"
                            value={formData.activitylevel}
                            options={ACTIVITY_LEVELS}
                            onChange={handleInputChange}
                        />

                        <SelectField
                            label="Fitness Goal"
                            id="fitnessgoal"
                            value={formData.fitnessgoal}
                            options={FITNESS_GOALS}
                            onChange={handleInputChange}
                        />

                        <CheckboxGroup
                            label="Food Restrictions"
                            name="foodrestrictions"
                            options={FOOD_RESTRICTIONS}
                            selectedValues={formData.foodrestrictions}
                            onChange={handleCheckboxChange}
                        />

                        <SelectField
                            label="Caffeine Intake"
                            id="caffeineintake"
                            value={formData.caffeineintake}
                            options={CAFFEINE_INTAKE}
                            onChange={handleInputChange}
                        />

                        <InputField
                            label="Average Sleep (Hours)"
                            id="averagesleep"
                            type="number"
                            value={formData.averagesleep}
                            onChange={handleInputChange}
                            min="0"
                        />

                        <SelectField
                            label="Sleep Quality"
                            id="sleepquality"
                            value={formData.sleepquality}
                            options={SLEEP_QUALITY}
                            onChange={handleInputChange}
                        />

                        <CheckboxGroup
                            label="Supplement Usage"
                            name="supplementusage"
                            options={SUPPLEMENT_USAGE}
                            selectedValues={formData.supplementusage}
                            onChange={handleCheckboxChange}
                        />

                        <SelectField
                            label="Supplement Frequency"
                            id="supplementfrequency"
                            value={formData.supplementfrequency}
                            options={SUPPLEMENT_FREQUENCY}
                            onChange={handleInputChange}
                        />

                        <button
                            className={styles.button}
                            type="submit"
                            disabled={isSaving}
                        >
                            {isSaving ? 'Saving...' : 'Save Preferences'}
                        </button>
                    </>
                )}
            </form>
        </Modal>
    );
}
