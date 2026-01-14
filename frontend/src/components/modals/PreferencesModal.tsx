'use client';

import React from 'react';
import Modal from '@/components/ui/Modal';
import { getPreferences, savePreferences } from '@/lib/api';
import type { Preferences } from '@/lib/types';
import { useModalForm } from '@/hooks/useModalForm';
import styles from '@/styles/components/Modal.module.css';

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

    const isChecked = (fieldName: string, value: string): boolean => {
        const fieldValue = formData[fieldName as keyof Preferences] as string || '';
        return fieldValue.split(', ').includes(value);
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
                        {/* Food Preference */}
                        <div className={styles.setting}>
                            <label>Food Preference:</label>
                            <div>
                                <input
                                    type="radio"
                                    name="foodpreference"
                                    value="Veg"
                                    checked={formData.foodpreference === 'Veg'}
                                    onChange={(e) => handleRadioChange('foodpreference', e.target.value)}
                                />
                                <label>Vegetarian</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="foodpreference"
                                    value="Non-Veg"
                                    checked={formData.foodpreference === 'Non-Veg'}
                                    onChange={(e) => handleRadioChange('foodpreference', e.target.value)}
                                />
                                <label>Non-Vegetarian</label>
                            </div>
                        </div>

                        {/* Snack Preferences */}
                        <div className={styles.setting}>
                            <label>Snack Preferences:</label>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('snackpreferences', 'Healthy')}
                                    onChange={(e) => handleCheckboxChange('snackpreferences', 'Healthy', e.target.checked)}
                                />
                                <label>Healthy Snacks</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('snackpreferences', 'High-Protein')}
                                    onChange={(e) => handleCheckboxChange('snackpreferences', 'High-Protein', e.target.checked)}
                                />
                                <label>High-Protein Snacks</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('snackpreferences', 'Low-Calorie')}
                                    onChange={(e) => handleCheckboxChange('snackpreferences', 'Low-Calorie', e.target.checked)}
                                />
                                <label>Low-Calorie Snacks</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('snackpreferences', 'No-Snacks')}
                                    onChange={(e) => handleCheckboxChange('snackpreferences', 'No-Snacks', e.target.checked)}
                                />
                                <label>No Snacks</label>
                            </div>
                        </div>

                        {/* Meal Timings */}
                        <div className={styles.setting}>
                            <label>Meal Timings:</label>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('mealtimings', 'Breakfast')}
                                    onChange={(e) => handleCheckboxChange('mealtimings', 'Breakfast', e.target.checked)}
                                />
                                <label>Breakfast</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('mealtimings', 'Lunch')}
                                    onChange={(e) => handleCheckboxChange('mealtimings', 'Lunch', e.target.checked)}
                                />
                                <label>Lunch</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('mealtimings', 'Dinner')}
                                    onChange={(e) => handleCheckboxChange('mealtimings', 'Dinner', e.target.checked)}
                                />
                                <label>Dinner</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('mealtimings', 'Frequent-Small-Meals')}
                                    onChange={(e) => handleCheckboxChange('mealtimings', 'Frequent-Small-Meals', e.target.checked)}
                                />
                                <label>Frequent Small Meals</label>
                            </div>
                        </div>

                        {/* Cheat Day Frequency */}
                        <div className={styles.setting}>
                            <label>Cheat Day Frequency:</label>
                            <div>
                                <input
                                    type="radio"
                                    name="cheatdayfrequency"
                                    value="None"
                                    checked={formData.cheatdayfrequency === 'None'}
                                    onChange={(e) => handleRadioChange('cheatdayfrequency', e.target.value)}
                                />
                                <label>No Cheat Days</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="cheatdayfrequency"
                                    value="Weekly"
                                    checked={formData.cheatdayfrequency === 'Weekly'}
                                    onChange={(e) => handleRadioChange('cheatdayfrequency', e.target.value)}
                                />
                                <label>Weekly</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="cheatdayfrequency"
                                    value="Biweekly"
                                    checked={formData.cheatdayfrequency === 'Biweekly'}
                                    onChange={(e) => handleRadioChange('cheatdayfrequency', e.target.value)}
                                />
                                <label>Biweekly (Every 2 Weeks)</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="cheatdayfrequency"
                                    value="Monthly"
                                    checked={formData.cheatdayfrequency === 'Monthly'}
                                    onChange={(e) => handleRadioChange('cheatdayfrequency', e.target.value)}
                                />
                                <label>Monthly</label>
                            </div>
                        </div>

                        {/* Cultural/Regional Preferences */}
                        <div className={styles.setting}>
                            <label>Cultural/Regional Food Preferences:</label>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('culturalpreferences', 'North Indian')}
                                    onChange={(e) => handleCheckboxChange('culturalpreferences', 'North Indian', e.target.checked)}
                                />
                                <label>North Indian</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('culturalpreferences', 'South Indian')}
                                    onChange={(e) => handleCheckboxChange('culturalpreferences', 'South Indian', e.target.checked)}
                                />
                                <label>South Indian</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('culturalpreferences', 'East Indian')}
                                    onChange={(e) => handleCheckboxChange('culturalpreferences', 'East Indian', e.target.checked)}
                                />
                                <label>East Indian</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('culturalpreferences', 'West Indian')}
                                    onChange={(e) => handleCheckboxChange('culturalpreferences', 'West Indian', e.target.checked)}
                                />
                                <label>West Indian</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('culturalpreferences', 'Global')}
                                    onChange={(e) => handleCheckboxChange('culturalpreferences', 'Global', e.target.checked)}
                                />
                                <label>Global Cuisine</label>
                            </div>
                        </div>

                        {/* Preferred Ingredients/Superfoods */}
                        <div className={styles.setting}>
                            <label>Preferred Ingredients / Superfoods:</label>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('preferredingredients', 'Quinoa')}
                                    onChange={(e) => handleCheckboxChange('preferredingredients', 'Quinoa', e.target.checked)}
                                />
                                <label>Quinoa</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('preferredingredients', 'Flax Seeds')}
                                    onChange={(e) => handleCheckboxChange('preferredingredients', 'Flax Seeds', e.target.checked)}
                                />
                                <label>Flax Seeds</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('preferredingredients', 'Chia Seeds')}
                                    onChange={(e) => handleCheckboxChange('preferredingredients', 'Chia Seeds', e.target.checked)}
                                />
                                <label>Chia Seeds</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('preferredingredients', 'Almonds')}
                                    onChange={(e) => handleCheckboxChange('preferredingredients', 'Almonds', e.target.checked)}
                                />
                                <label>Almonds</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('preferredingredients', 'Moringa')}
                                    onChange={(e) => handleCheckboxChange('preferredingredients', 'Moringa', e.target.checked)}
                                />
                                <label>Moringa</label>
                            </div>
                            <div>
                                <input
                                    type="checkbox"
                                    checked={isChecked('preferredingredients', 'Ghee')}
                                    onChange={(e) => handleCheckboxChange('preferredingredients', 'Ghee', e.target.checked)}
                                />
                                <label>Ghee</label>
                            </div>
                        </div>

                        {/* Cuisine Preferences */}
                        <div className={styles.setting}>
                            <label>Cuisine Preferences:</label>
                            {['Indian', 'Continental', 'Mediterranean', 'Chinese', 'Italian', 'Mexican', 'Thai', 'Japanese', 'Middle Eastern'].map((cuisine) => (
                                <div key={cuisine}>
                                    <input
                                        type="checkbox"
                                        checked={isChecked('cuisinepreferences', cuisine)}
                                        onChange={(e) => handleCheckboxChange('cuisinepreferences', cuisine, e.target.checked)}
                                    />
                                    <label>{cuisine}</label>
                                </div>
                            ))}
                        </div>

                        {/* Spicy Food Tolerance */}
                        <div className={styles.setting}>
                            <label htmlFor="spicytolerance">Spicy Food Tolerance:</label>
                            <select
                                id="spicytolerance"
                                value={formData.spicyfoodtolerance}
                                onChange={(e) => handleInputChange('spicyfoodtolerance', e.target.value)}
                            >
                                <option value="Low">Low</option>
                                <option value="Medium">Medium</option>
                                <option value="High">High</option>
                            </select>
                        </div>

                        {/* Preferred Meal Type */}
                        <div className={styles.setting}>
                            <label htmlFor="mealtype">Preferred Meal Type:</label>
                            <select
                                id="mealtype"
                                value={formData.preferredmealtype}
                                onChange={(e) => handleInputChange('preferredmealtype', e.target.value)}
                            >
                                <option value="Light">Light</option>
                                <option value="Heavy">Heavy</option>
                            </select>
                        </div>

                        {/* Favorite Meal */}
                        <div className={styles.setting}>
                            <label htmlFor="favoritemeal">Favorite Meal:</label>
                            <select
                                id="favoritemeal"
                                value={formData.favoritemeal}
                                onChange={(e) => handleInputChange('favoritemeal', e.target.value)}
                            >
                                <option value="Breakfast">Breakfast</option>
                                <option value="Lunch">Lunch</option>
                                <option value="Dinner">Dinner</option>
                            </select>
                        </div>

                        {/* Meal Frequency */}
                        <div className={styles.setting}>
                            <label>Meal Frequency:</label>
                            <div>
                                <input
                                    type="radio"
                                    name="mealfrequency"
                                    value="2"
                                    checked={formData.mealfrequency === '2'}
                                    onChange={(e) => handleRadioChange('mealfrequency', e.target.value)}
                                />
                                <label>2 meals/day</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="mealfrequency"
                                    value="3"
                                    checked={formData.mealfrequency === '3'}
                                    onChange={(e) => handleRadioChange('mealfrequency', e.target.value)}
                                />
                                <label>3 meals/day</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="mealfrequency"
                                    value="5-6"
                                    checked={formData.mealfrequency === '5-6'}
                                    onChange={(e) => handleRadioChange('mealfrequency', e.target.value)}
                                />
                                <label>5-6 small meals</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="mealfrequency"
                                    value="Intermittent Fasting"
                                    checked={formData.mealfrequency === 'Intermittent Fasting'}
                                    onChange={(e) => handleRadioChange('mealfrequency', e.target.value)}
                                />
                                <label>Intermittent Fasting</label>
                            </div>
                        </div>

                        {/* Sweet Preference */}
                        <div className={styles.setting}>
                            <label>Sweet Preference:</label>
                            <div>
                                <input
                                    type="radio"
                                    name="sweetpreference"
                                    value="No Sugar"
                                    checked={formData.sweetpreference === 'No Sugar'}
                                    onChange={(e) => handleRadioChange('sweetpreference', e.target.value)}
                                />
                                <label>No Sugar</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="sweetpreference"
                                    value="Low Sugar"
                                    checked={formData.sweetpreference === 'Low Sugar'}
                                    onChange={(e) => handleRadioChange('sweetpreference', e.target.value)}
                                />
                                <label>Low Sugar</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="sweetpreference"
                                    value="Regular Sugar"
                                    checked={formData.sweetpreference === 'Regular Sugar'}
                                    onChange={(e) => handleRadioChange('sweetpreference', e.target.value)}
                                />
                                <label>Regular Sugar</label>
                            </div>
                        </div>

                        {/* Eating Out Frequency */}
                        <div className={styles.setting}>
                            <label>Eating Out Frequency:</label>
                            <div>
                                <input
                                    type="radio"
                                    name="eatingout"
                                    value="Never"
                                    checked={formData.eatingoutfrequency === 'Never'}
                                    onChange={(e) => handleRadioChange('eatingoutfrequency', e.target.value)}
                                />
                                <label>Never</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="eatingout"
                                    value="Rarely"
                                    checked={formData.eatingoutfrequency === 'Rarely'}
                                    onChange={(e) => handleRadioChange('eatingoutfrequency', e.target.value)}
                                />
                                <label>Rarely</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    name="eatingout"
                                    value="Often"
                                    checked={formData.eatingoutfrequency === 'Often'}
                                    onChange={(e) => handleRadioChange('eatingoutfrequency', e.target.value)}
                                />
                                <label>Often</label>
                            </div>
                        </div>

                        {/* Hydration Level */}
                        <div className={styles.setting}>
                            <label htmlFor="hydration">Daily Water Intake (L):</label>
                            <input
                                type="number"
                                id="hydration"
                                min="0"
                                value={formData.hydrationlevel || ''}
                                onChange={(e) => handleInputChange('hydrationlevel', parseFloat(e.target.value) || 0)}
                            />
                        </div>

                        {/* Preferred Drinks */}
                        <div className={styles.setting}>
                            <label>Preferred Drinks:</label>
                            {['Water', 'Tea', 'Coffee'].map((drink) => (
                                <div key={drink}>
                                    <input
                                        type="checkbox"
                                        checked={isChecked('preferreddrinks', drink)}
                                        onChange={(e) => handleCheckboxChange('preferreddrinks', drink, e.target.checked)}
                                    />
                                    <label>{drink}</label>
                                </div>
                            ))}
                        </div>

                        {/* Activity Level */}
                        <div className={styles.setting}>
                            <label htmlFor="activitylevel">Activity Level:</label>
                            <select
                                id="activitylevel"
                                value={formData.activitylevel}
                                onChange={(e) => handleInputChange('activitylevel', e.target.value)}
                            >
                                <option value="Sedentary">Sedentary</option>
                                <option value="Lightly Active">Lightly Active</option>
                                <option value="Moderately Active">Moderately Active</option>
                                <option value="Very Active">Very Active</option>
                            </select>
                        </div>

                        {/* Fitness Goal */}
                        <div className={styles.setting}>
                            <label htmlFor="fitnessgoal">Fitness Goal:</label>
                            <select
                                id="fitnessgoal"
                                value={formData.fitnessgoal}
                                onChange={(e) => handleInputChange('fitnessgoal', e.target.value)}
                            >
                                <option value="Weight Loss">Weight Loss</option>
                                <option value="Muscle Gain">Muscle Gain</option>
                                <option value="Maintenance">Maintenance</option>
                                <option value="General Well-being">General Well-being</option>
                            </select>
                        </div>

                        {/* Food Restrictions */}
                        <div className={styles.setting}>
                            <label>Food Restrictions:</label>
                            {['Nuts', 'Gluten', 'Dairy', 'Eggs', 'Shellfish', 'Peanuts', 'Low-Carb', 'Low-Sodium', 'Halal', 'Kosher'].map((restriction) => (
                                <div key={restriction}>
                                    <input
                                        type="checkbox"
                                        checked={isChecked('foodrestrictions', restriction)}
                                        onChange={(e) => handleCheckboxChange('foodrestrictions', restriction, e.target.checked)}
                                    />
                                    <label>{restriction === 'Dairy' ? 'No Dairy (Vegan-Friendly)' : `${restriction === 'Gluten' ? 'Gluten-Free' : restriction === 'Nuts' || restriction === 'Eggs' || restriction === 'Shellfish' || restriction === 'Peanuts' ? `No ${restriction}` : restriction}`}</label>
                                </div>
                            ))}
                        </div>

                        {/* Caffeine Intake */}
                        <div className={styles.setting}>
                            <label htmlFor="caffeine">Caffeine Intake:</label>
                            <select
                                id="caffeine"
                                value={formData.caffeineintake}
                                onChange={(e) => handleInputChange('caffeineintake', e.target.value)}
                            >
                                <option value="None">None</option>
                                <option value="Low">Low</option>
                                <option value="Moderate">Moderate</option>
                                <option value="High">High</option>
                            </select>
                        </div>

                        {/* Sleep */}
                        <div className={styles.setting}>
                            <label htmlFor="sleep">Average Sleep (Hours):</label>
                            <input
                                type="number"
                                id="sleep"
                                min="0"
                                value={formData.averagesleep || ''}
                                onChange={(e) => handleInputChange('averagesleep', parseFloat(e.target.value) || 0)}
                            />
                        </div>

                        <div className={styles.setting}>
                            <label htmlFor="sleepquality">Sleep Quality:</label>
                            <select
                                id="sleepquality"
                                value={formData.sleepquality}
                                onChange={(e) => handleInputChange('sleepquality', e.target.value)}
                            >
                                <option value="Poor">Poor</option>
                                <option value="Average">Average</option>
                                <option value="Good">Good</option>
                            </select>
                        </div>

                        {/* Supplement Usage */}
                        <div className={styles.setting}>
                            <label>Supplement Usage:</label>
                            {['Multivitamin', 'Protein', 'Other'].map((supplement) => (
                                <div key={supplement}>
                                    <input
                                        type="checkbox"
                                        checked={isChecked('supplementusage', supplement)}
                                        onChange={(e) => handleCheckboxChange('supplementusage', supplement, e.target.checked)}
                                    />
                                    <label>{supplement}</label>
                                </div>
                            ))}
                        </div>

                        <div className={styles.setting}>
                            <label htmlFor="supplementfreq">Supplement Frequency:</label>
                            <select
                                id="supplementfreq"
                                value={formData.supplementfrequency}
                                onChange={(e) => handleInputChange('supplementfrequency', e.target.value)}
                            >
                                <option value="Daily">Daily</option>
                                <option value="Weekly">Weekly</option>
                                <option value="Occasionally">Occasionally</option>
                            </select>
                        </div>


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
