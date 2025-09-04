/**
 * Configuration utilities
 */

export interface Config {
  [key: string]: any;
}

export const getEnvVar = (name: string, defaultValue?: string): string => {
  const value = process.env[name];
  if (!value && defaultValue === undefined) {
    throw new Error(`Environment variable ${name} is required but not set`);
  }
  return value || defaultValue || '';
};

export const getEnvVarAsNumber = (name: string, defaultValue?: number): number => {
  const value = process.env[name];
  if (!value && defaultValue === undefined) {
    throw new Error(`Environment variable ${name} is required but not set`);
  }
  const parsed = value ? parseInt(value, 10) : defaultValue;
  if (parsed === undefined || isNaN(parsed)) {
    throw new Error(`Environment variable ${name} must be a number`);
  }
  return parsed;
};

export const getEnvVarAsBoolean = (name: string, defaultValue?: boolean): boolean => {
  const value = process.env[name];
  if (!value && defaultValue === undefined) {
    throw new Error(`Environment variable ${name} is required but not set`);
  }
  if (!value) return defaultValue || false;
  return value.toLowerCase() === 'true' || value === '1';
};

export const loadConfig = (prefix: string = ''): Config => {
  const config: Config = {};
  const prefixWithUnderscore = prefix ? `${prefix}_` : '';
  
  Object.keys(process.env).forEach(key => {
    if (key.startsWith(prefixWithUnderscore)) {
      const configKey = key.substring(prefixWithUnderscore.length).toLowerCase();
      config[configKey] = process.env[key];
    }
  });
  
  return config;
};