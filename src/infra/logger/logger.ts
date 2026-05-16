import pino from 'pino';

const isProduction = process.env.NODE_ENV === 'production';

/**
 * Pino logger instance configured for the application.
 *
 * - Log level is set via `LOG_LEVEL` environment variable (default: 'info').
 * - In non-production environments, uses `pino-pretty` for human-readable output.
 */
export const logger = pino({
    level: process.env.LOG_LEVEL || 'info',
    transport: !isProduction ? {
        target: 'pino-pretty',
        options: {
            colorize: true,
            translateTime: 'HH:MM:ss',
            ignore: 'pid,hostname'
        }
    }
    : undefined
});