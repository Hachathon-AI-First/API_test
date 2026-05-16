import { Request, Response, NextFunction } from 'express';

export function apiAuth(
    req: Request,
    res: Response,
    next: NextFunction
) {
    const log = (req as any).log;
    const authHeader = req.headers.authorization;
    const expectedToken = process.env.API_SECRET;

    if (!expectedToken) {
        log.error('API_SECRET not set');
        return res.status(500).json({ error: 'Server misconfigured' });
    }

    if (!authHeader) {
        log?.warn('API auth failed: Authorization header missing');
        return res.status(401).json({ error: 'Unauthorized' });
    }

    const [type, token] = authHeader.split(' ');
    
    if (type !== 'Bearer' || token !== expectedToken) {
        log?.warn('API auth failed: invalid token');
        return res.status(401).json({ error: 'Unauthorized' });
    }

    if (token.trim() !== expectedToken.trim()) {
        log?.warn('API auth failed: invalid token');
        return res.status(401).json({ error: 'Unauthorized' });
    }

    next();
}