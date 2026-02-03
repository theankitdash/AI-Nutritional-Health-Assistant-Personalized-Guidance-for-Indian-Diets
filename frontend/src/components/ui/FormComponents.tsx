import React from 'react';
import styles from '@/styles/components/Modal.module.css';

interface Option {
    value: string;
    label: string;
}

interface RadioGroupProps {
    label: string;
    name: string;
    options: Option[];
    selectedValue: string;
    onChange: (name: string, value: string) => void;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({ label, name, options, selectedValue, onChange }) => (
    <div className={styles.setting}>
        <label>{label}:</label>
        {options.map((option) => (
            <div key={option.value}>
                <input
                    type="radio"
                    name={name}
                    value={option.value}
                    checked={selectedValue === option.value}
                    onChange={(e) => onChange(name, e.target.value)}
                />
                <label>{option.label}</label>
            </div>
        ))}
    </div>
);

interface CheckboxGroupProps {
    label: string;
    name: string;
    options: Option[];
    selectedValues: string; // Comma separated string
    onChange: (name: string, value: string, checked: boolean) => void;
}

export const CheckboxGroup: React.FC<CheckboxGroupProps> = ({ label, name, options, selectedValues, onChange }) => {
    const isChecked = (value: string) => {
        const valuesArray = selectedValues ? selectedValues.split(', ') : [];
        return valuesArray.includes(value);
    };

    return (
        <div className={styles.setting}>
            <label>{label}:</label>
            {options.map((option) => (
                <div key={option.value}>
                    <input
                        type="checkbox"
                        checked={isChecked(option.value)}
                        onChange={(e) => onChange(name, option.value, e.target.checked)}
                    />
                    <label>{option.label}</label>
                </div>
            ))}
        </div>
    );
};

interface SelectFieldProps {
    label: string;
    id: string;
    value: string;
    options: Option[];
    onChange: (name: string, value: string) => void;
    disabled?: boolean;
}

export const SelectField: React.FC<SelectFieldProps> = ({ label, id, value, options, onChange, disabled }) => (
    <div className={styles.setting}>
        <label htmlFor={id}>{label}:</label>
        <select
            id={id}
            value={value}
            onChange={(e) => onChange(id, e.target.value)}
            disabled={disabled}
        >
            {options.map((option) => (
                <option key={option.value} value={option.value}>
                    {option.label}
                </option>
            ))}
        </select>
    </div>
);

interface InputFieldProps {
    label: string;
    id: string;
    type?: string;
    value: string | number;
    onChange: (name: string, value: string | number) => void;
    placeholder?: string;
    min?: string;
    disabled?: boolean;
}

export const InputField: React.FC<InputFieldProps> = ({ label, id, type = 'text', value, onChange, placeholder, min, disabled }) => (
    <div className={styles.setting}>
        <label htmlFor={id}>{label}:</label>
        <input
            type={type}
            id={id}
            value={value}
            min={min}
            onChange={(e) => onChange(id, type === 'number' ? (parseFloat(e.target.value) || 0) : e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
        />
    </div>
);
