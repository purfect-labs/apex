/**
 * Environment Constants - Standardized environments for APEX UI
 * These are the only valid environments throughout the application
 */

// Standard environments used throughout the UI
export const ENVIRONMENTS = {
    DEV: 'dev',
    STAGE: 'stage', 
    PROD: 'prod'
};

// Array of all environments for iteration
export const ENVIRONMENT_LIST = [
    ENVIRONMENTS.DEV,
    ENVIRONMENTS.STAGE,
    ENVIRONMENTS.PROD
];

// Environment display names
export const ENVIRONMENT_NAMES = {
    [ENVIRONMENTS.DEV]: 'Development',
    [ENVIRONMENTS.STAGE]: 'Staging',
    [ENVIRONMENTS.PROD]: 'Production'
};

// Environment colors for UI
export const ENVIRONMENT_COLORS = {
    [ENVIRONMENTS.DEV]: '#00ff88',
    [ENVIRONMENTS.STAGE]: '#ffaa00',
    [ENVIRONMENTS.PROD]: '#ff4444'
};

// Validate environment
export function isValidEnvironment(env) {
    return ENVIRONMENT_LIST.includes(env);
}

// Get environment display name
export function getEnvironmentName(env) {
    return ENVIRONMENT_NAMES[env] || env;
}

// Get environment color
export function getEnvironmentColor(env) {
    return ENVIRONMENT_COLORS[env] || '#888888';
}