import { v4 as uuid } from 'uuid';
import { logger } from './logger.js';

/**
 * Middleware to attach a Pino logger instance to each request.
 *
 * - Generates a unique request ID for tracing.
 * - Attaches a child logger (`req.log`) with contextual information (request ID, method, path).
 * - Logs the start of the request.
 * - Logs the completion of the request (including status code) when the response finishes.
 *
 * @param req - Express request-like object.
 * @param res - Express response-like object.
 * @param next - Express next function to call after middleware execution.
 */
export function requestLogger(req: any, res: any, next: any) {
    const requestId = uuid();

    req.log = logger.child({
        requestId,
        method: req.method,
        path: req.path, 
    });

    req.log.info('Incoming request');

    res.on('finish', () => {
        req.log.info(
            { statusCode: res.statusCode },
            'Request completed'
        );
    });

    next();
}