import { logger, LogLevel, createLogger } from '../../src/logger';
import { getEnvVar, loadConfig } from '../../src/config';
import { isEmail, isUrl, createValidator } from '../../src/validation';
import { ValidationError, NotFoundError } from '../../src/errors';

describe('Shared Utils', () => {
  describe('Logger', () => {
    it('should create a logger', () => {
      const testLogger = createLogger(LogLevel.DEBUG);
      expect(testLogger).toBeDefined();
      expect(typeof testLogger.info).toBe('function');
    });

    it('should have default logger', () => {
      expect(logger).toBeDefined();
      expect(typeof logger.info).toBe('function');
    });
  });

  describe('Config', () => {
    beforeEach(() => {
      delete process.env.TEST_VAR;
    });

    it('should get environment variable with default', () => {
      const value = getEnvVar('TEST_VAR', 'default');
      expect(value).toBe('default');
    });

    it('should load config with prefix', () => {
      process.env.APP_NAME = 'test';
      process.env.APP_PORT = '3000';
      const config = loadConfig('APP');
      expect(config.name).toBe('test');
      expect(config.port).toBe('3000');
    });
  });

  describe('Validation', () => {
    it('should validate email', () => {
      expect(isEmail('test@example.com')).toBe(true);
      expect(isEmail('invalid-email')).toBe(false);
    });

    it('should validate URL', () => {
      expect(isUrl('https://example.com')).toBe(true);
      expect(isUrl('invalid-url')).toBe(false);
    });

    it('should create validator', () => {
      const validator = createValidator<string>();
      validator.addRule({
        validate: (value) => value.length > 0,
        message: 'Value cannot be empty'
      });

      const result = validator.validate('test');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('Errors', () => {
    it('should create ValidationError', () => {
      const error = new ValidationError('Invalid input', 'email');
      expect(error).toBeInstanceOf(ValidationError);
      expect(error.message).toBe('Invalid input');
      expect(error.field).toBe('email');
      expect(error.statusCode).toBe(400);
    });

    it('should create NotFoundError', () => {
      const error = new NotFoundError('User');
      expect(error).toBeInstanceOf(NotFoundError);
      expect(error.message).toBe('User not found');
      expect(error.statusCode).toBe(404);
    });
  });
});
